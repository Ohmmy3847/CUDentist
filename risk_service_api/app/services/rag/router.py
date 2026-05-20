"""
Query Router — Category Classifier
====================================
Classifies an incoming patient query into a corpus category so that
retrieve_and_rerank can scope its ChromaDB search accordingly.

Categories:
  post_op_care  — questions about what to do / avoid after a dental procedure
  general_info  — general dental knowledge, procedure explanations, etc.
  None          — ambiguous; search all categories (safe fallback)
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Category definitions sent to the LLM ─────────────────────────────────────
_CATEGORIES = {
    "post_op_care": (
        "Questions about home care, recovery, activity restrictions, diet, "
        "medications, pain/swelling management, or wound care AFTER a dental "
        "procedure (extraction, wisdom tooth removal, jaw surgery, etc.)."
    ),
    "general_info": (
        "Questions about dental procedures themselves, costs, causes of "
        "conditions, anatomy, or information not specific to post-op recovery."
    ),
}

_PROMPT = """\
You are a query router for a dental post-operative care assistant.

Classify the patient question below into exactly one category.

Categories:
{categories}

Patient question: "{question}"
{context_hint}

Reply ONLY with a JSON object: {{"category": "<category_name>"}}
If the question could belong to multiple categories or is unclear, reply: {{"category": null}}
"""


async def classify_query_category(
    question: str,
    patient_context: Optional[dict] = None,
) -> Optional[str]:
    """
    Returns "post_op_care", "general_info", or None (search all).
    Never raises — falls back to None on any error.
    """
    from app.core.factory import ModelFactory

    cat_text = "\n".join(
        f'  "{k}": {v}' for k, v in _CATEGORIES.items()
    )
    context_hint = ""
    if patient_context:
        procedures = (
            patient_context.get("patient_profile", {}).get("procedures", [])
        )
        if procedures:
            context_hint = f'Patient had procedure(s): {", ".join(procedures)}'

    prompt = _PROMPT.format(
        categories=cat_text,
        question=question,
        context_hint=context_hint,
    )

    try:
        llm = ModelFactory.get_llm(use_case="rag")
        response = await llm.ainvoke(prompt)
        raw = response.content.strip()

        # Extract JSON even if wrapped in markdown
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning(f"[Router] Could not parse JSON from: {raw!r}")
            return None

        data = json.loads(match.group())
        category = data.get("category")

        if category not in _CATEGORIES and category is not None:
            logger.warning(f"[Router] Unknown category '{category}' — falling back to None")
            return None

        logger.info(f"[Router] '{question[:60]}' → category={category}")
        return category

    except Exception as e:
        logger.warning(f"[Router] Classification failed: {e} — using no filter")
        return None
