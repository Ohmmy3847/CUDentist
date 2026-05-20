import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.rag.retriever import retrieve_and_rerank
from app.services.rag.validator import validate_chunks
from app.services.rag.pipeline import answer_patient_question
from app.core.factory import ModelFactory

logging.basicConfig(level=logging.WARNING)

# ── Test case ─────────────────────────────────────────────────────────────────
QUESTION = "ถอนฟันกรามกี่วันหายปวด"
PATIENT_CONTEXT = {
    "patient_profile": {
        "procedures": ["ถอนฟัน (Extraction)"],
        "days_post_op": 1,
    },
    "current_symptoms": {},
    "risk_assessment": {
        "overall_risk": "ความเสี่ยงต่ำ",
        "flows": {},
    },
}
# ─────────────────────────────────────────────────────────────────────────────


async def test_retrieval_debug():
    print(f"Question: {QUESTION}")

    embedding_function = ModelFactory.get_embeddings(use_case="rag")
    retrieved_chunks = await retrieve_and_rerank(QUESTION, embedding_function, PATIENT_CONTEXT)

    print(f"\n=== Chunks BEFORE Validation ({len(retrieved_chunks)}) ===")
    for i, chunk in enumerate(retrieved_chunks):
        src = chunk.metadata.get("source", "?")[:50]
        print(f"\n--- [{i+1}] {src} ---")
        print(chunk.page_content.strip())

    valid_chunks = await validate_chunks(QUESTION, retrieved_chunks)

    print(f"\n=== Chunks AFTER Validation ({len(valid_chunks)}) ===")
    for i, chunk in enumerate(valid_chunks):
        src = chunk.metadata.get("source", "?")[:50]
        print(f"\n--- [{i+1}] {src} ---")
        print(chunk.page_content.strip())

    print("\n" + "=" * 60)
    print("=== FINAL ANSWER ===")
    print("=" * 60)
    result = await answer_patient_question(QUESTION, PATIENT_CONTEXT)
    print(f"Source: {result['source']}")
    print(f"\n{result['answer']}")


if __name__ == "__main__":
    asyncio.run(test_retrieval_debug())
