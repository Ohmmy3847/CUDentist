"""
Validator for Post-Op Patient Q&A
──────────────────────────────────
Stricter relevance filtering + parallel LLM calls
"""
import asyncio
import logging
from typing import List
from langchain_core.documents import Document
from app.core.factory import ModelFactory
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

VALIDATION_PROMPT = PromptTemplate.from_template(
    "คุณเป็นผู้ตรวจสอบความเกี่ยวข้องของข้อมูลทางทันตกรรม\n\n"
    "คำถาม: '{question}'\n\n"
    "ข้อความ:\n{text}\n\n"
    "ข้อความนี้มีข้อมูลที่อาจเป็นประโยชน์ต่อการตอบคำถามหรือไม่?\n\n"
    "YES ถ้า: มีสาเหตุ, อาการ, ขั้นตอนการดูแล, คำแนะนำ, ข้อมูลทางการแพทย์ที่เกี่ยวข้อง หรือข้อมูลประกอบที่เป็นประโยชน์ในบริบทเดียวกัน\n"
    "NO ถ้า: เป็นแค่ชื่อเรื่อง, โฆษณา, ราคา, ลิงก์, หรือไม่เกี่ยวข้องกับคำถามเลย\n\n"
    "เมื่อไม่แน่ใจ ให้ตอบ YES\n"
    "ตอบ YES หรือ NO เท่านั้น"
)


async def _validate_one(
    chain, question: str, chunk: Document, index: int
) -> tuple[int, bool]:
    """Validate a single chunk (for parallel execution)."""
    try:
        response = await chain.ainvoke({
            "question": question,
            "text": chunk.page_content,
        })
        answer = response.content.strip().upper()
        is_valid = "YES" in answer
        logger.debug(f"  Chunk {index + 1}: {'✓ YES' if is_valid else '✗ NO'} | {chunk.page_content[:60]}...")
        return (index, is_valid)
    except Exception as e:
        logger.error(f"  Chunk {index + 1} validation error: {e}")
        return (index, False)


async def validate_chunks(question: str, chunks: List[Document]) -> List[Document]:
    """
    Validate all chunks in PARALLEL with a stricter prompt.
    Only keeps chunks with specific, actionable information.
    """
    if not chunks:
        return []

    logger.debug(f"Validating {len(chunks)} chunks (parallel)...")
    llm = ModelFactory.get_llm(use_case="rag")
    chain = VALIDATION_PROMPT | llm

    # Fire all validations in parallel
    tasks = [
        _validate_one(chain, question, chunk, i)
        for i, chunk in enumerate(chunks)
    ]
    results = await asyncio.gather(*tasks)

    # Collect valid chunks in original order
    valid_indices = {idx for idx, is_valid in results if is_valid}
    valid_chunks = [chunk for i, chunk in enumerate(chunks) if i in valid_indices]

    logger.debug(f"Validation complete: {len(valid_chunks)}/{len(chunks)} chunks kept.")
    return valid_chunks
