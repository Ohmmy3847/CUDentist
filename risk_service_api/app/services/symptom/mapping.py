"""
Custom Symptom Mapping Service
================================
Retrieval + Strict LLM Classification pipeline

Pipeline (per symptom segment):
  1. Embed query  →  cosine similarity vs ChromaDB (bge-m3 via OpenRouter)
  2. Retrieve top-5 candidates
  3. LLM classifies: pick the best match from top-5, or reject if none match
     - LLM is strict: precision must be 1 (never return a wrong match)
     - Prefer rejection over incorrect match
  4. Multi-symptom: split free text → multiple segments → map each independently

Dependencies (ต้องมีใน env):
  OPEN_ROUTER_API_KEY   - for embeddings (BAAI/bge-m3 via OpenRouter)
  DEEPSEEK_API_KEY      - for LLM classification
  CHROMA_DB_PATH        - path to ChromaDB directory
  CSV_PATH              - path to Custom_Symptom.csv
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import concurrent.futures
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import chromadb
import numpy as np
from dotenv import load_dotenv
import sys

# Ensure service root is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.core.factory import ModelFactory
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", os.path.join(DATA_DIR, "chroma_db"))
CSV_PATH = os.getenv("CSV_PATH", os.path.join(DATA_DIR, "Custom_Symptom.csv"))

# ─── Retry / rate-limit guard ──────────────────────────────────────────────────
EMBED_RETRY_DELAY: float = 1.0  # seconds between embedding retries
MAX_EMBED_RETRIES: int = 3


# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class Candidate:
    """ผลลัพธ์จาก ChromaDB สำหรับ 1 candidate"""
    symptom: str
    metadata: Dict[str, Any]
    similarity: float
    distance: float


@dataclass
class MappingResult:
    """ผลการ map อาการ 1 segment"""
    query: str                            # คำที่ผู้ใช้พิมพ์มา
    matched: bool                         # เจอหรือไม่
    matched_symptom: str = ""             # symptom canonical label
    similarity: float = 0.0              # cosine similarity score
    tier: str = "rejected"               # "llm" | "rejected"
    risk_level: str = ""
    recommendation: str = ""
    management: str = ""
    reason: str = ""
    candidates_inspected: int = 0        # จำนวน candidates ที่ตรวจสอบ


# ─── Embedding ────────────────────────────────────────────────────────────────

def get_embedding(text: str) -> np.ndarray:
    """
    เรียก Embeddings ผ่าน ModelFactory (รองรับ OpenRouter, OpenAI, Ollama)
    """
    try:
        embeddings = ModelFactory.get_embeddings(use_case="symptom")
        vec = embeddings.embed_query(text)
        return np.array(vec, dtype=np.float32)
    except Exception as e:
        logger.error(f"[Embed] Error getting embedding: {e}")
        raise RuntimeError(f"Failed to get embedding: {e}")


# ─── ChromaDB retrieval ───────────────────────────────────────────────────────

def retrieve_candidates(
    query: str,
    collection: chromadb.Collection,
    top_k: int = 5,
) -> List[Candidate]:
    """
    ดึง top-k candidates จาก ChromaDB (cosine similarity)
    คืนค่าเรียงตาม similarity descending
    """
    query_vec = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_vec.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    candidates: List[Candidate] = []
    # Type guard: ensure results contain expected data
    if results and results["documents"] and results["metadatas"] and results["distances"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            sim = max(0.0, 1.0 - dist)  # cosine distance → similarity
            # Cast metadata to Dict[str, Any] for type compatibility
            metadata_dict: Dict[str, Any] = dict(meta) if meta else {}
            candidates.append(Candidate(symptom=doc, metadata=metadata_dict, similarity=sim, distance=dist))

    # sort desc by similarity
    candidates.sort(key=lambda c: c.similarity, reverse=True)
    return candidates


# ─── LLM Classification ──────────────────────────────────────────────────────

_LLM_SYSTEM_PROMPT = """\
You are a medical triage classifier for a dental post-operative care system.
Your job: given a patient's symptom description and 5 candidate labels from a database,
decide if ANY candidate truly matches the patient's core symptom.

RULES:
  1. A match means the patient's CORE symptom is semantically identical to the candidate label —
     same body part AND same symptom type. The patient may use more words or synonyms.
     Example: "ยาที่ต้องกินขมมาก" → "ยาขม" → MATCH (same core symptom).
  2. Synonyms, paraphrases, and Thai/English variations ARE valid matches when the meaning is truly the same.
     "เลือดไหล" and "มีเลือดออก" → MATCH.
  3. Do NOT match if the symptom differs in body part, cause, or type — even if words partially overlap.
     Shared adjectives (เจ็บ, แห้ง, คัน) do NOT make two symptoms a match if the underlying condition differs.
     "ปวดหัว" → "ปวดฟัน" → NOT a match. "คอแห้ง" → "ปากแห้ง" → NOT a match (different anatomy).
  4. If the patient's input is not a dental/medical symptom or is nonsensical → reject.
  5. When in doubt, return match=false. A false rejection is safer than a false match.

Respond ONLY with a JSON object (no markdown, no explanation):
{"match": true/false, "matched_symptom": "<exact label string from candidates, or null>", "reason": "<one sentence in Thai or English>"}
"""


def llm_classify(query: str, candidates: List[Candidate], language: str = "th") -> Tuple[bool, Optional["Candidate"], str]:
    """
    ส่ง query + top-5 candidates ให้ LLM classify best match
    LLM เป็น strict classifier — ต้อง match จริงๆ เท่านั้น (precision=1)
    Returns (is_match, matched_candidate_or_None, reason)
    """
    candidate_lines = "\n".join(
        f"  {i+1}. \"{c.symptom}\" (similarity: {c.similarity:.4f})"
        for i, c in enumerate(candidates)
    )
    user_msg = (
        f"Patient input: \"{query}\"\n\n"
        f"Candidate symptom labels (top-{len(candidates)} from database):\n{candidate_lines}\n\n"
        f"Does any candidate truly match the patient's symptom? "
        f"Remember: when in doubt, return match=false. "
        f"A wrong match is worse than a missed match."
    )

    try:
        llm = ModelFactory.get_llm(temperature=0.0, use_case="symptom")
        messages = [
            SystemMessage(content=_LLM_SYSTEM_PROMPT),
            HumanMessage(content=user_msg)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        logger.debug(f"[LLM Classify] raw: {content}")

        content = re.sub(r"```(?:json)?\s*([\s\S]*?)```", r"\1", content).strip()
        parsed = json.loads(content)
        is_match = bool(parsed.get("match", False))
        reason = str(parsed.get("reason", ""))
        matched_label = parsed.get("matched_symptom")

        matched_candidate = None
        if is_match and matched_label:
            matched_candidate = next(
                (c for c in candidates if c.symptom == matched_label), None
            )
            if matched_candidate is None:
                # LLM returned a label not in candidates → treat as rejection
                logger.warning(f"[LLM Classify] Label '{matched_label}' not in candidates → rejecting")
                return False, None, "LLM returned unknown label"
        logger.info(f"[LLM Classify] '{query}' → '{matched_label}' match={is_match}")
        return is_match, matched_candidate, reason

    except json.JSONDecodeError as e:
        logger.error(f"[LLM Classify] JSON parse error: {e}. Content: {content}")
        return False, None, "LLM response parse error"
    except Exception as e:
        logger.error(f"[LLM Classify] Error: {e}")
        return False, None, f"LLM error: {str(e)[:80]}"


# ─── Risk level mapping ───────────────────────────────────────────────────────

_RISK_LEVEL_MAP_TH = {
    "ต่ำ": "ความเสี่ยงต่ำ",
    "ปานกลาง": "ความเสี่ยงปานกลาง",
    "สูง": "ความเสี่ยงสูง",
    "ซับซ้อน": "ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน",
}

_RISK_LEVEL_MAP_EN = {
    "ต่ำ": "Low Risk",
    "ปานกลาง": "Medium Risk",
    "สูง": "High Risk",
    "ซับซ้อน": "Complicated",
}


def _map_risk_level(raw: str, language: str = "th") -> str:
    mapping = _RISK_LEVEL_MAP_TH if language == "th" else _RISK_LEVEL_MAP_EN
    raw = str(raw).strip()
    return mapping.get(raw, raw)


def _safe_str(value: Any, fallback: str = "") -> str:
    s = str(value).strip()
    return fallback if s in ("", "nan", "None") else s


def _llm_translate_to_en(fields: Dict[str, str]) -> Dict[str, str]:
    """Translate Thai dental/medical text fields to English via LLM (single call)."""
    non_empty = {k: v for k, v in fields.items() if v.strip()}
    if not non_empty:
        return fields
    try:
        llm = ModelFactory.get_llm(temperature=0.0, use_case="symptom")
        fields_json = json.dumps(non_empty, ensure_ascii=False)
        prompt = (
            f"Translate the following Thai dental/medical text fields to English.\n"
            f"Return ONLY a JSON object with the same keys and translated values.\n"
            f"Keep translations concise and clinical. Do not add explanations.\n\n"
            f"{fields_json}"
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        content = re.sub(r"```(?:json)?\s*([\s\S]*?)```", r"\1", response.content.strip()).strip()
        translated = json.loads(content)
        return {k: str(translated.get(k, v)) for k, v in fields.items()}
    except Exception as e:
        logger.warning(f"[Translate] Error: {e}. Using original Thai text.")
        return fields


# ─── Multi-symptom text splitter ─────────────────────────────────────────────

# Delimiters สำหรับ fallback regex split
_SYMPTOM_DELIMITERS = re.compile(
    r"[,،،\n\r;/]|(?:\s+และ\s+)|(?:\s+and\s+)|(?:\s+กับ\s+)|(?:\s+with\s+)",
    flags=re.IGNORECASE,
)

_LLM_EXTRACT_SYSTEM_PROMPT = """\
You are a medical NLP assistant. Extract individual symptom phrases from the user's input.
Return ONLY a JSON array of strings. Each element is one symptom phrase (keep original wording).
Do NOT translate, do NOT summarize.

Input format: one or more objects with 'symptom' and 'detail' fields.

Steps:
1. Split each 'symptom' field into individual symptom phrases if it contains multiple symptoms.
2. For each symptom, decide how to use 'detail':
   - If 'detail' describes WHEN/HOW the symptom occurs (e.g. "ตอนกินน้ำ", "หลังตื่นนอน") → append detail to that symptom
   - If 'detail' describes the relationship BETWEEN symptoms (e.g. "เป็นงี้พร้อมกัน", "สลับกัน") → do NOT append, keep symptoms separate
   - If 'detail' is empty or irrelevant → ignore it
3. Preserve original language and wording of every symptom.

Examples:
  Input: {'symptom': 'ปวดหัวมาก แล้วก็เวียนหัว คลื่นไส้นิดหน่อย', 'detail': 'เป็นงี้พร้อมกัน'}
  → detail บอก relationship ระหว่าง symptom → ไม่ append
  Output: ["ปวดหัวมาก", "เวียนหัว", "คลื่นไส้นิดหน่อย"]

  Input: {'symptom': 'แสบคอ', 'detail': 'สักพักก็หาย'}
  → detail บอก how symptom behaves → append
  Output: ["แสบคอสักพักก็หาย"]

  Input: {'symptom': 'แสบคอ', 'detail': 'ตอนกินน้ำ'}
  → detail บอก when symptom occurs → append
  Output: ["แสบคอตอนกินน้ำ"]

  Input: {'symptom': 'my throat hurts and I have a dry mouth', 'detail': ''}
  → detail ว่าง → ไม่ append
  Output: ["my throat hurts", "dry mouth"]

  Input: {'symptom': 'ปวดท้อง คลื่นไส้', 'detail': 'หลังกินข้าว'}
  → detail บอก when → append ทุก symptom
  Output: ["ปวดท้องหลังกินข้าว", "คลื่นไส้หลังกินข้าว"]

  Input: {'symptom': 'ปวดหัว มีไข้', 'detail': 'สลับกัน'}
  → detail บอก relationship → ไม่ append
  Output: ["ปวดหัว", "มีไข้"]

  Input: {'symptom': 'เห็นพี่คอหักอยู่ตรงห้องน้ำดังกร็อบแกร็ปค่ะ', 'detail': ''}
  → symtom เอาแค่อาการ ไม่เอาคำพูด และไม่เอาคำลงท้าย
  Output: ["คอหักดังกร็อบแกร็ป"]

  Input: [{'symptom': 'ปวดหัวมาก แล้วก็เวียนหัว คลื่นไส้นิดหน่อย', 'detail': 'เป็นงี้พร้อมกัน'}, {'symptom': 'แสบคอ', 'detail': 'สักพักก็หาย'}, {'symptom': 'my throat hurts and I have a dry mouth', 'detail': ''}]
  Output: ["ปวดหัวมาก", "เวียนหัว", "คลื่นไส้นิดหน่อย", "แสบคอสักพักก็หาย", "my throat hurts", "dry mouth"]

Edge cases:
  - If 'symptom' is empty → skip that object entirely
  - If output has only one symptom → still return as array: ["..."]
  - Do NOT deduplicate symptoms
"""


def llm_extract_symptoms(text: str) -> List[str]:
    """
    ใช้ LLM แยก symptom phrases จาก free text
    Fallback to regex split ถ้า LLM ไม่ available หรือ error

    Returns:
        list of symptom phrase strings (original wording)
    """
    try:
        llm = ModelFactory.get_llm(temperature=0.0, use_case="symptom")
        messages = [
            SystemMessage(content=_LLM_EXTRACT_SYSTEM_PROMPT),
            HumanMessage(content=text)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        logger.debug(f"[LLM Extract] raw: {content}")

        # strip markdown code block
        content = re.sub(r"```(?:json)?\s*([\s\S]*?)```", r"\1", content).strip()
        phrases = json.loads(content)

        if isinstance(phrases, list) and all(isinstance(p, str) for p in phrases):
            result = [p.strip() for p in phrases if p.strip()]
            logger.info(f"[LLM Extract] '{text}' → {result}")
            return result if result else _regex_split(text)
        else:
            logger.warning("[LLM Extract] Unexpected format, using regex fallback.")
            return _regex_split(text)

    except Exception as e:
        logger.warning(f"[LLM Extract] Error: {e}. Using regex fallback.")
        return _regex_split(text)


def _regex_split(text: str, min_length: int = 2) -> List[str]:
    """Regex-based fallback splitter"""
    if not text or not text.strip():
        return []
    parts = _SYMPTOM_DELIMITERS.split(text)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) >= min_length]


# ─── Core mapping function ────────────────────────────────────────────────────

def map_symptom(
    query: str,
    collection: chromadb.Collection,
    top_k: int = 5,
    language: str = "th",
    enable_llm: bool = True,
) -> MappingResult:
    """
    Map อาการเดี่ยว 1 segment: retrieve top-5 → LLM classify → accept or reject
    LLM is strict: precision=1, prefer rejection over wrong match.
    """
    query = query.strip()
    if not query:
        return MappingResult(query=query, matched=False, tier="rejected", reason="empty query")

    # ── Retrieve top-5 candidates ──────────────────────────────────────────────
    try:
        candidates = retrieve_candidates(query, collection, top_k=top_k)
    except Exception as e:
        logger.error(f"[map_symptom] Retrieve error for '{query}': {e}")
        return MappingResult(query=query, matched=False, tier="rejected", reason=f"retrieval error: {str(e)[:80]}")

    if not candidates:
        return MappingResult(query=query, matched=False, tier="rejected", reason="no candidates returned")

    # ── Print top-k candidates (debug) ────────────────────────────────────────
    logger.info(f"  Top-{len(candidates)} Candidates for '{query}':")
    for i, c in enumerate(candidates, 1):
        logger.info(f"      {i}. '{c.symptom}'  sim={c.similarity:.4f}")

    # ── LLM Classification (always) ───────────────────────────────────────────
    _comp_risk = (
        "ไม่สามารถสรุปผลความเสี่ยงได้เนื่องจากอาการมีความซับซ้อน" if language == "th" else "Complicated"
    )
    _comp_rec = (
        "ควรปรึกษาพยาบาลหรือทันตแพทย์เพื่อประเมินอาการเพิ่มเติม" if language == "th"
        else "Talk to your nurse or dentist for a check-up"
    )

    if not enable_llm:
        # LLM disabled — cannot classify, reject
        return MappingResult(
            query=query, matched=False, tier="rejected",
            risk_level=_comp_risk, recommendation=_comp_rec,
            reason="LLM disabled, cannot classify",
            candidates_inspected=len(candidates),
        )

    is_match, matched_candidate, reason = llm_classify(query, candidates, language)

    if not is_match or matched_candidate is None:
        return MappingResult(
            query=query, matched=False, tier="rejected",
            risk_level=_comp_risk, recommendation=_comp_rec,
            reason=reason or "LLM rejected all candidates",
            candidates_inspected=len(candidates),
        )

    # ── Build successful result ────────────────────────────────────────────────
    top = matched_candidate
    meta = top.metadata
    risk_raw = _safe_str(meta.get("Risk level", meta.get("risk_level", "")), "ต่ำ")
    recommendation = _safe_str(meta.get("Recommendation", meta.get("recommendation", "")))
    management = _safe_str(meta.get("Management", meta.get("management", "")))
    matched_symptom = top.symptom

    if language == "en":
        translated = _llm_translate_to_en({
            "matched_symptom": matched_symptom,
            "recommendation": recommendation,
            "management": management,
        })
        matched_symptom = translated.get("matched_symptom", matched_symptom)
        recommendation = translated.get("recommendation", recommendation)
        management = translated.get("management", management)

    return MappingResult(
        query=query,
        matched=True,
        matched_symptom=matched_symptom,
        similarity=top.similarity,
        tier="llm",
        risk_level=_map_risk_level(risk_raw, language),
        recommendation=recommendation,
        management=management,
        reason=reason,
        candidates_inspected=len(candidates),
    )


# ─── Multi-symptom mapping ────────────────────────────────────────────────────

def _extract_original_phrases(free_text: str) -> List[str]:
    """
    Extract the original symptom phrases from the input before LLM splitting.

    If free_text is a JSON array of {symptom, detail} objects (from the form),
    return each non-empty symptom+detail concatenation as an original phrase.
    For plain strings return [free_text] itself.
    """
    stripped = free_text.strip()
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            parsed = json.loads(stripped)
            if not isinstance(parsed, list):
                parsed = [parsed]
            phrases = []
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                symptom = (item.get("symptom") or "").strip()
                detail  = (item.get("detail")  or "").strip()
                if symptom:
                    phrase = f"{symptom} {detail}".strip() if detail else symptom
                    phrases.append(phrase)
            return phrases
        except (json.JSONDecodeError, TypeError):
            pass
    # Plain string — use as-is
    return [stripped] if stripped else []


def map_symptoms(
    free_text: str,
    collection: chromadb.Collection,
    top_k: int = 5,
    language: str = "th",
    enable_llm: bool = True,
) -> List[MappingResult]:
    """
    Map free text ที่อาจมีหลายอาการ → list of MappingResult

    Pipeline:
      Step 1 [LLM Extract]:  LLM แยก symptom phrases → fallback: regex split
      Step 1b [Fallback guard]: เพิ่ม original phrases เผื่อ LLM split ผิด
      Step 2 [Per-segment]:  retrieve top-5 → LLM classify ต่อ segment
      Step 3 [Dedup]:        collapse ผลลัพธ์ที่ canonical label เดียวกัน
    """
    free_text = free_text.strip()
    if not free_text:
        return [MappingResult(query=free_text, matched=False, tier="rejected", reason="empty input")]

    # ── Step 1: LLM symptom extraction ─────────────────────────────────────────
    if enable_llm:
        print(f"\n  🤖 LLM extracting symptoms from: \"{free_text}\"")
        segments = llm_extract_symptoms(free_text)
        print(f"  📌 Extracted: {segments}")
    else:
        segments = _regex_split(free_text)

    if not segments:
        return [MappingResult(query=free_text, matched=False, tier="rejected", reason="no valid segments")]

    # ── Step 1b: Fallback guard — also try original phrases ────────────────────
    # If LLM split a phrase, the original unsplit text is added as an extra
    # candidate so a wrong split doesn't lose a valid match.
    original_phrases = _extract_original_phrases(free_text)
    already = {s.strip().lower() for s in segments}
    for phrase in original_phrases:
        if phrase.strip().lower() not in already and len(phrase.strip()) >= 2:
            segments.append(phrase)
            logger.debug(f"[map_symptoms] Added original phrase as fallback: '{phrase}'")

    # ── Step 2: Map each segment ───────────────────────────────────────────────
    raw_results: List[MappingResult] = []
    if segments:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(segments))) as executor:
            future_to_seg = {
                executor.submit(map_symptom, seg, collection, top_k, language, enable_llm): seg 
                for seg in segments
            }
            for future in concurrent.futures.as_completed(future_to_seg):
                try:
                    result = future.result()
                    raw_results.append(result)
                except Exception as e:
                    seg = future_to_seg[future]
                    logger.error(f"[map_symptoms] Error processing segment '{seg}': {e}")
                    raw_results.append(MappingResult(query=seg, matched=False, tier="rejected", reason=f"error: {str(e)[:80]}"))

    # ── Step 3: Dedup matched results by canonical label ──────────────────────
    seen: Dict[str, MappingResult] = {}
    for r in raw_results:
        if r.matched:
            existing = seen.get(r.matched_symptom)
            if existing is None or r.similarity > existing.similarity:
                seen[r.matched_symptom] = r
    final = list(seen.values()) + [r for r in raw_results if not r.matched]
    final.sort(key=lambda r: (not r.matched, -r.similarity))
    return final


# ─── Convenience API ──────────────────────────────────────────────────────────

def get_collection(*args, **kwargs) -> chromadb.Collection:
    """Get ChromaDB 'symptoms' collection (HttpClient → PersistentClient fallback)."""
    from app.services.rag.chunker import _get_chroma_client
    client = _get_chroma_client()
    return client.get_or_create_collection(
        name="symptoms",
        metadata={"hnsw:space": "cosine"},
    )



def map_free_text(
    text: str,
    language: str = "th",
    enable_llm: bool = True,
) -> List[Dict[str, Any]]:
    """
    Convenience wrapper: map free text ที่มีหลายอาการ → list of dict
    """
    collection = get_collection()
    results = map_symptoms(text, collection, top_k=5, language=language, enable_llm=enable_llm)
    return [_result_to_dict(r, language) for r in results]


def _result_to_dict(result: MappingResult, language: str = "th") -> Dict[str, Any]:
    """แปลง MappingResult → dict (backward-compatible format)"""
    if not result.matched:
        # ใช้ค่าจาก MappingResult โดยตรง (ถูก set แล้วใน map_symptom())
        fallback_reason = (
            f"มีอาการอื่นๆที่ผู้ป่วยระบุเพิ่มเติม: {result.query}"
            if language == "th"
            else f"Additional symptoms reported: {result.query}"
        )
        return {
            "matched": False,
            "tier": result.tier,
            "query": result.query,
            "similarity": 0.0,
            "matched_symptom": "",
            "risk_level": result.risk_level,
            "reason": fallback_reason,
            "recommendation": result.recommendation,
            "management": "",
        }

    return {
        "matched": True,
        "tier": result.tier,
        "query": result.query,
        "similarity": round(result.similarity, 4),
        "matched_symptom": result.matched_symptom,
        "risk_level": result.risk_level,
        "reason": result.reason,
        "recommendation": result.recommendation,
        "management": result.management,
    }


# ─── Ingestion ───────────────────────────────────────────────────────────────

def ingest(reset: bool = False):
    """
    Ingest Custom_Symptom.csv into ChromaDB 'symptoms' collection.
    """
    import pandas as pd
    from tqdm import tqdm
    import sys
    
    logger.info("═══ Starting symptom ingestion process ═══")
    if not os.path.exists(CSV_PATH):
        logger.error(f"CSV file not found: {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    if 'Symptoms' not in df.columns:
        logger.error("CSV does not contain 'Symptoms' column.")
        sys.exit(1)

    symptoms = df['Symptoms'].tolist()
    
    from app.core.config import settings
    client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection_name = "symptoms"

    if reset:
        logger.warning(f"Reset mode: deleting collection '{collection_name}' …")
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"  ✓ Collection '{collection_name}' deleted.")
        except Exception:
            logger.info(f"  Collection '{collection_name}' does not exist — nothing to delete.")

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    logger.info("Generating embeddings for symptoms...")
    
    # ── ใช้ Batch Embedding แทนการรันทีละอัน ──
    embedding_function = ModelFactory.get_embeddings(use_case="symptom")
    embeddings = embedding_function.embed_documents(symptoms)

    ids = [str(i) for i in range(len(symptoms))]
    
    logger.info(f"Adding {len(symptoms)} symptoms to ChromaDB...")
    collection.add(
        embeddings=embeddings,
        documents=symptoms,
        ids=ids,
        metadatas=df.to_dict(orient="records")
    )
    logger.info("✓ ChromaDB updated for symptoms.")


# ─── CLI / quick test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # ─── CLI / quick test ─────────────────────────────────────────────────────────

    #python app/services/symptom/mapping.py --ingest --reset
    #python app/services/symptom/mapping.py --test "คอหัก"

    import sys
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(description="Custom Symptom Mapping & Ingestion Pipeline")
    parser.add_argument("--ingest", action="store_true", help="Run ingestion from CSV to ChromaDB")
    parser.add_argument("--reset", action="store_true", help="Delete 'symptoms' collection before re-ingesting")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--test", type=str, help="Test mapping with a free-text symptom query")
    args = parser.parse_args()

    # If ingest mode is triggered
    if args.ingest:
        print("=====================================================")
        print("🦷 Symptom Mapping Ingestion (ChromaDB)")
        print("=====================================================")
        if args.reset:
            print("⚠️  WARNING: You selected --reset. The old 'symptoms' collection will be DELETED.")
        else:
            print("ℹ️  INFO: You did not select --reset. New data will be APPENDED.")
        print(f"📦 Source Data: {CSV_PATH}")

        if not args.yes:
            confirm = input("\nDo you want to proceed with ingestion? (y/n) [y]: ").strip().lower()
            if confirm not in ('', 'y', 'yes'):
                print("Abort: Ingestion cancelled by user.")
                sys.exit(0)
        
        try:
            ingest(reset=args.reset)
            sys.exit(0)
        except KeyboardInterrupt:
            print("\nAbort: System interrupted.")
            sys.exit(1)

    # Testing mode
    if args.test:
        single_inputs = [args.test]
    else:
        single_inputs = ["คอหัก"]
    
    print("=" * 70)
    print("Custom Symptom Mapping — Top-5 + Strict LLM Classify")
    from app.core.config import settings
    print(f"  LLM_MODEL    = {settings.MODEL_NAME_SYMPTOM}")
    print("=" * 70)

    try:
        col = get_collection()
    except Exception as e:
        print(f"[ERROR] Cannot connect to ChromaDB: {e}")
        sys.exit(1)

    print("\n" + "─" * 70)
    print("MULTI-SYMPTOM MODE  (LLM extraction → per-segment mapping)")
    print("─" * 70)
    for text in single_inputs:
        print(f"\n{'='*70}")
        print(f"> Input: \"{text}\"")
        results = map_symptoms(text, col, language="th", enable_llm=True)
        for r in results:
            status = f"[{r.tier.upper()}]" if r.matched else "[REJECT]"
            print(f"  {status} '{r.query}' → '{r.matched_symptom}' sim={r.similarity:.4f}")
            print(f"        risk: {r.risk_level}")
            if not r.matched:
                print(f"        why:  {r.reason}")
