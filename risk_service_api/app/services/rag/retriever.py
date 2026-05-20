"""
Retriever and Reranker for Post-Op Patient Q&A
──────────────────────────────────────────────
Flow: Context Query → Single Hybrid Search → Deduplicate → FlashRank rerank → Diversity select
"""
import asyncio
import logging
from typing import List, Set
from langchain_core.documents import Document
from langchain_chroma import Chroma
import pickle

from app.services.rag.chunker import CHROMADB_DIR, COLLECTION_NAME
from app.services.common.thai_tokenizer import bm25_thai_preprocess  # noqa: F401 — needed for pickle unpickle
from app.core.factory import ModelFactory
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

logger = logging.getLogger(__name__)

# ── Tunables ─────────────────────────────────────────────────────────
INITIAL_K             = 50  # docs from hybrid search
RERANK_TOP_K          = 15  # docs returned after reranking
MAX_CHUNKS_PER_SOURCE = 3   # max chunks from the same source file in final results

# ── Reranker (multilingual cross-encoder, supports Thai) ─────────────
_reranker = None

def _get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")
        logger.info("[retriever] Loaded cross-encoder reranker: bge-reranker-v2-m3")
    return _reranker


def build_context_query(question: str, patient_context: dict | None) -> str:
    """Deterministically prepend procedure + days_post_op to the question.

    Examples:
        No context  → "วันนี้กินอะไรได้บ้าง?"
        With context → "ผ่าตัดขากรรไกร BSSRO วันที่ 3 หลังผ่าตัด: วันนี้กินอะไรได้บ้าง?"
    """
    if not patient_context:
        return question
    profile = patient_context.get("patient_profile", {})
    procedures = profile.get("procedures", [])
    days = profile.get("days_post_op")
    prefix_parts = []
    if procedures:
        prefix_parts.append(" ".join(procedures))
    if days is not None:
        prefix_parts.append(f"วันที่ {days} หลังผ่าตัด")
    if prefix_parts:
        return " ".join(prefix_parts) + ": " + question
    return question


def get_chroma_vectorstore(embedding_function) -> Chroma:
    """Get the Chroma vectorstore."""
    from app.services.rag.chunker import _get_chroma_client
    return Chroma(
        collection_name=COLLECTION_NAME,
        client=_get_chroma_client(),
        embedding_function=embedding_function,
    )


def get_bm25_retriever() -> BM25Retriever:
    """Load BM25 Retriever from disk if exists."""
    import pickle
    bm25_path = CHROMADB_DIR / "bm25_index.pkl"
    if bm25_path.exists():
        with open(bm25_path, 'rb') as f:
            return pickle.load(f)
    logger.warning(f"BM25 index not found at {bm25_path}. Run chunker.py to build it.")
    return None


# =====================================================================
#  LLM #1: Query Rewriting
# =====================================================================
async def rewrite_query(question: str, patient_context: dict = None) -> str:
    """
    LLM #1: Query Rewriting
    ปรับปรุงคำถามให้มีความชัดเจน สมบูรณ์ และเป็นทางการมากขึ้น โดยอาศัยบริบทผู้ป่วย (ถ้ามี)
    """
    llm = ModelFactory.get_llm(use_case="rag")
    
    context_text = ""
    if patient_context:
        import json
        profile = patient_context.get("patient_profile", {})
        symptoms = patient_context.get("current_symptoms", {})
        if profile or symptoms:
            context_text = "\nข้อมูลผู้ป่วยระดับบริบท:\n"
            if profile:
                context_text += f"- ประวัติ: {json.dumps(profile, ensure_ascii=False)}\n"
            if symptoms:
                context_text += f"- อาการ: {json.dumps(symptoms, ensure_ascii=False)}\n"
            context_text += "\n"

    prompt = (
        "คุณเป็นผู้เชี่ยวชาญด้านทันตกรรม\n"
        "หน้าที่ของคุณคือการปรับปรุงคำถามของผู้ป่วยให้มีความชัดเจน กระชับ สมบูรณ์ และตรงประเด็นมากที่สุด "
        "เพื่อนำไปใช้ค้นหาในฐานข้อมูลต่อไป (Query Rewriting)\n"
        f"คำถามดั้งเดิม: \"{question}\"\n"
        f"{context_text}"
        "เงื่อนไข:\n"
        "1. หากคำถามไม่ชัดเจนหรือขาดประธาน ให้ใช้ข้อมูลบริบทผู้ป่วยมาช่วยขยายความให้สมบูรณ์ (เช่น 'ต้องกินนานแค่ไหน' เปลี่ยนเป็น 'ต้องกินยาชื่อ...นานแค่ไหน')\n"
        "2. หากคำถามชัดเจนดีแล้ว ให้จำกัดความให้เหมาะสมสำหรับการค้นหา\n"
        "3. ตอบกลับเฉพาะ 'คำถามที่ถูกปรับปรุงแล้ว' เพียง 1 ประโยค ห้ามมีคำอธิบายเพิ่มเติม ห้ามมีเครื่องหมายคำพูด\n\n"
        "คำถามที่ถูกปรับปรุง:"
    )

    try:
        response = await llm.ainvoke(prompt)
        rewritten = response.content.strip()
        rewritten = rewritten.strip('"\'')
        logger.info(f"Query rewriting: '{question}' -> '{rewritten}'")
        return rewritten if rewritten else question
    except Exception as e:
        logger.error(f"Query rewriting failed: {e}")
        return question


# =====================================================================
#  LLM #2: Query Decomposition
# =====================================================================
async def decompose_query(question: str) -> List[str]:
    """
    LLM #2: Query Decomposition
    แตกคำถามที่มีหลายประเด็นซ้อนกัน (Multi-intent) ออกเป็นคำถามย่อยๆ
    """
    llm = ModelFactory.get_llm(use_case="rag")
    
    prompt = (
        "คุณคือระบบตรรกะวิเคราะห์คำถาม\n"
        "หน้าที่ของคุณคือการตรวจสอบว่าคำถามเป้าหมาย ประกอบด้วยคำถามย่อยประเด็นที่ต่างกันหลายเรื่องซ่อนอยู่หรือไม่ (Query Decomposition)\n"
        f"คำถาม: \"{question}\"\n\n"
        "เงื่อนไข:\n"
        "1. หากคำถามมีหลายประเด็นผสมกันอย่างชัดเจน (เช่น ถามทั้งเรื่องการจัดฟัน และการทำความสะอาด) ให้แยกออกมาเป็นคำถามย่อยทีละประเด็น\n"
        "2. หากคำถามมีประเด็นหลักเพียงประเด็นเดียว ให้ตอบกลับเป็นประโยคเดิมเท่านั้น\n"
        "3. ตอบกลับ 1 บรรทัด ต่อ 1 คำถามย่อย (ห้ามพิมพ์ตัวเลขนำหน้า ห้ามใส่คำอธิบาย ห้ามใช้ Bullet point หรือสัญลักษณ์ใดๆ ทุกกรณี)\n\n"
        "คำตอบ:"
    )

    try:
        response = await llm.ainvoke(prompt)
        lines = [l.strip().lstrip("-*123456789. ") for l in response.content.strip().split("\n")]
        decomposed = [l for l in lines if l and len(l) > 3]
        
        if not decomposed:
            decomposed = [question]
            
        logger.info(f"Query decomposition: '{question}' -> {len(decomposed)} sub-queries: {decomposed}")
        return decomposed
    except Exception as e:
        logger.error(f"Query decomposition failed: {e}")
        return [question]


# =====================================================================
#  LLM #3: Query Expansion
# =====================================================================
async def expand_query(question: str, patient_context: dict = None) -> List[str]:
    """
    LLM #3: Query Expansion
    Use DeepSeek to generate alternative search queries.
    Returns the original question + N expanded queries.
    """
    llm = ModelFactory.get_llm(use_case="rag")
    
    # Format the patient context for the prompt
    context_text = ""
    if patient_context:
        import json
        profile = patient_context.get("patient_profile", {})
        symptoms = patient_context.get("current_symptoms", {})
        if profile or symptoms:
            context_text = "\nข้อมูลผู้ป่วยปัจจุบันที่เกี่ยวข้อง (ใช้ประกอบการพิจารณาสร้างคำค้นหา):\n"
            if profile:
                context_text += f"- ประวัติการรักษา/ผ่าตัด: {json.dumps(profile, ensure_ascii=False)}\n"
            if symptoms:
                context_text += f"- อาการปัจจุบัน: {json.dumps(symptoms, ensure_ascii=False)}\n"
            context_text += "\n"

    prompt = (
        "คุณเป็นผู้เชี่ยวชาญด้านการค้นหาข้อมูลทางการแพทย์ทันตกรรม\n"
        f"คำถามเดิม: \"{question}\"\n"
        f"{context_text}"
        f"สร้างคำค้นหาที่แตกต่างกัน {NUM_EXPANSIONS} แบบ เพื่อค้นหาข้อมูลในเอกสารวิชาการทันตกรรม\n"
        "โดยอิงจากคำถามเดิม และหากมีข้อมูลอาการ/ประวัติผู้ป่วย ให้นำไปเรียบเรียงเป็นคำค้นหาที่สอดคล้องกับสภาวะนั้นด้วย\n"
        "แต่ละแบบควรใช้คำศัพท์หรือมุมมองที่ต่างกัน (เช่น ใช้ชื่อทางการ, ใช้ภาษาชาวบ้าน, เน้นคนละแง่มุม)\n\n"
        "ตอบเฉพาะคำค้นหา โดยแต่ละอันขึ้นบรรทัดใหม่ ไม่ต้องใส่หมายเลข ไม่ต้องอธิบาย"
    )

    try:
        response = await llm.ainvoke(prompt)
        lines = [l.strip().lstrip("0123456789.-) ") for l in response.content.strip().split("\n")]
        expanded = [l for l in lines if l and len(l) > 5][:NUM_EXPANSIONS]
        all_queries = [question] + expanded
        logger.info(f"Query expansion: {len(all_queries)} queries → {all_queries}")
        return all_queries
    except Exception as e:
        logger.error(f"Query expansion failed: {e}")
        return [question]


# =====================================================================
#  Deduplication
# =====================================================================
def deduplicate_docs(docs: List[Document]) -> List[Document]:
    """Remove near-duplicate documents based on content similarity."""
    seen: Set[str] = set()
    unique: List[Document] = []

    for doc in docs:
        # Strip the [SOURCE: ...] header before fingerprinting
        # so chunks with same content from different sources are detected as duplicates
        content = doc.page_content.strip()
        if content.startswith("[SOURCE:"):
            # Skip past the header line to get actual content
            newline_idx = content.find("\n")
            if newline_idx != -1:
                content = content[newline_idx + 1:].strip()
        fingerprint = content[:150]
        if fingerprint not in seen:
            seen.add(fingerprint)
            unique.append(doc)

    removed = len(docs) - len(unique)
    if removed > 0:
        logger.info(f"  Deduplication: removed {removed} duplicates ({len(docs)} → {len(unique)})")
    return unique


def _extract_content(text: str) -> str:
    """Strip [SOURCE: ...] header from chunk to get actual content."""
    text = text.strip()
    if text.startswith("[SOURCE:"):
        newline_idx = text.find("\n")
        if newline_idx != -1:
            return text[newline_idx + 1:].strip()
    return text


def _jaccard_similarity(text_a: str, text_b: str) -> float:
    """Character trigram Jaccard similarity (works for Thai without tokenizer)."""
    def trigrams(text):
        text = text.strip()
        return {text[i:i+3] for i in range(len(text) - 2)} if len(text) >= 3 else {text}
    
    set_a = trigrams(text_a)
    set_b = trigrams(text_b)
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def diversity_select(reranked_results: list, top_k: int) -> list:
    """Select top_k results, capping chunks per source to MAX_CHUNKS_PER_SOURCE."""
    selected = []
    source_counts: dict = {}

    for res in reranked_results:
        if len(selected) >= top_k:
            break
        source = res.get("meta", {}).get("source", "")
        if source_counts.get(source, 0) >= MAX_CHUNKS_PER_SOURCE:
            continue
        selected.append(res)
        source_counts[source] = source_counts.get(source, 0) + 1

    logger.info(f"  Diversity selection: {len(selected)}/{top_k} from {len(reranked_results)} candidates")
    return selected


# =====================================================================
#  Main Retrieval Pipeline
# =====================================================================
async def retrieve_and_rerank(
    question: str,
    embedding_function,
    patient_context: dict = None,
) -> List[Document]:
    """
    1) Build context-enriched query (deterministic, no LLM)
    2) Single hybrid search (ChromaDB dense 0.6 + BM25 0.4)
    3) Deduplicate
    4) FlashRank rerank
    5) Source-diversity selection → top-K
    """
    context_query = build_context_query(question, patient_context)
    logger.info(f"[retriever] context_query='{context_query}'")

    # 1. Hybrid search (single query)
    vectorstore = get_chroma_vectorstore(embedding_function)
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": INITIAL_K})
    bm25_retriever = get_bm25_retriever()

    if bm25_retriever:
        bm25_retriever.k = INITIAL_K
        retriever = EnsembleRetriever(
            retrievers=[dense_retriever, bm25_retriever],
            weights=[0.8, 0.2],
        )
        logger.info("[retriever] Using Hybrid Search (ChromaDB + BM25)")
    else:
        retriever = dense_retriever
        logger.info("[retriever] Using Dense Search only (ChromaDB)")

    all_docs = await retriever.ainvoke(context_query)
    logger.info(f"[retriever] {len(all_docs)} docs before dedup")

    if not all_docs:
        return []

    # 2. Deduplicate
    unique_docs = deduplicate_docs(all_docs)

    # 3. Source-diversity selection (hybrid score ordering)
    # Cross-encoder rerankers tested (mmarco, bge-reranker-v2-m3) both hurt coverage
    # on Thai dental Q&A — bge-m3 + BM25 hybrid ordering is already sufficient.
    top_docs = []
    source_counts: dict = {}
    for doc in unique_docs:
        if len(top_docs) >= RERANK_TOP_K:
            break
        source = doc.metadata.get("source", "")
        if source_counts.get(source, 0) >= MAX_CHUNKS_PER_SOURCE:
            continue
        top_docs.append(doc)
        source_counts[source] = source_counts.get(source, 0) + 1

    logger.info(f"[retriever] Returning {len(top_docs)} documents.")
    return top_docs
