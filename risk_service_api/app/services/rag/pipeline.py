"""
Main Pipeline for Post-Op Patient Q&A
"""
import logging
import json
from typing import Dict, Any, List
import asyncio
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from app.core.factory import ModelFactory
from app.services.rag.retriever import retrieve_and_rerank
from app.services.rag.validator import validate_chunks
from app.services.common.prompts import NURSE_QA_TEMPLATE, NURSE_SYSTEM_PROMPT
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

async def check_sufficiency(question: str, rule_based_context: dict) -> bool:
    """Check if rule-based context is sufficient to answer the question."""
    # Fast-path: if context is empty or has no real data, skip LLM call
    if not rule_based_context or all(
        v is None or v == "" or v == [] or v == {}
        for v in rule_based_context.values()
    ):
        logger.info("Sufficiency check result: NO (empty context)")
        return False

    llm = ModelFactory.get_llm(use_case="rag")
    prompt_str = (
        "You are a strict evaluator. You must decide whether the provided CONTEXT "
        "contains enough SPECIFIC information to FULLY answer the QUESTION.\n\n"
        "Rules:\n"
        "- If the context is empty, missing, or irrelevant → answer NO\n"
        "- If the context only partially answers the question → answer NO\n"
        "- Do NOT use your own medical knowledge. Only judge based on the given context.\n"
        "- Reply with ONLY 'YES' or 'NO', nothing else.\n\n"
        "CONTEXT:\n{context}\n\n"
        "QUESTION: {question}\n\n"
        "Answer:"
    )

    try:
        response = await llm.ainvoke(prompt_str.format(
            context=json.dumps(rule_based_context, ensure_ascii=False),
            question=question
        ))
        answer = response.content.strip().upper()
        logger.info(f"Sufficiency check result: {answer}")
        return "YES" in answer
    except Exception as e:
        logger.error(f"Error in sufficiency check: {e}")
        return False

async def answer_patient_question(
    question: str,
    patient_context: dict
) -> dict:
    """
    Main pipeline for answering patient questions.

    Args:
        question: Patient's question (from additional_questions)
        patient_context: Rich context from context_builder.build_patient_context()
            {
                "patient_profile": {...},
                "current_symptoms": {...},
                "risk_assessment": {...},
            }

    Returns: {"answer": str, "source": "rule_based" | "rag" | "Not enough information", "used_chunks": list}
    """
    logger.info(f"Answering patient question: '{question}'")

    risk_assessment = patient_context.get("risk_assessment", {})
    retrieved_chunks = []

    # 1. Check whether structured risk context is already sufficient
    is_sufficient = await check_sufficiency(question, risk_assessment)

    used_chunks = []
    rag_context_str = "ไม่มีข้อมูลเพิ่มเติม"
    source = ""
    if is_sufficient:
        source = "rule_based"
    else:
        # 2. Retrieve supporting context only when rule-based context is insufficient
        embedding_function = ModelFactory.get_embeddings(use_case="rag")
        retrieved_chunks = await retrieve_and_rerank(question, embedding_function, patient_context)

        # 3. Validate retrieved chunks
        valid_chunks = await validate_chunks(question, retrieved_chunks)

        if valid_chunks:
            source = "rag"
            used_chunks = [{"content": c.page_content, "metadata": c.metadata} for c in valid_chunks]
            rag_context_str = "\n\n".join([c.page_content for c in valid_chunks])
        else:
            source = "Not enough information"
            rag_context_str = "ไม่มีข้อมูลเพิ่มเติม (คำถามผู้ป่วยอาจอยู่นอกเหนือบริบท)"
            return {
                "answer": "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้องกับคำถามของคุณ กรุณาติดต่อพยาบาลเพื่อขอคำแนะนำเพิ่มเติม",
                "source": source,
                "used_chunks": used_chunks
            }

    # 4. Build final prompt with rich context
    prompt = ChatPromptTemplate.from_messages([
        ("system", NURSE_SYSTEM_PROMPT),
        ("human", NURSE_QA_TEMPLATE)
    ])
    
    chain = prompt | ModelFactory.get_llm(use_case="rag")

    # Format context sections
    patient_profile = patient_context.get("patient_profile", {})
    current_symptoms = patient_context.get("current_symptoms", {})
    recommendations = risk_assessment.get("recommendations", [])
    
    try:
        response = await chain.ainvoke({
            "patient_profile": json.dumps(patient_profile, ensure_ascii=False, indent=2) if patient_profile else "ไม่ระบุ",
            "current_symptoms": json.dumps(current_symptoms, ensure_ascii=False, indent=2) if current_symptoms else "ไม่ระบุ",
            "risk_level": risk_assessment.get("overall_risk", "ไม่ระบุ"),
            "recommendations": json.dumps(recommendations, ensure_ascii=False) if recommendations else "ไม่มี",
            "rag_context": rag_context_str,
            "question": question
        })
        final_answer = response.content.strip()
    except Exception as e:
        logger.error(f"Error generating final answer: {e}")
        final_answer = "ขออภัย เกิดข้อผิดพลาดในการประมวลผลคำตอบ ควรติดต่อทีมแพทย์โดยตรง"

    # Append multi-procedure disclaimer if patient has more than 1 procedure
    procedures = patient_profile.get("procedures", [])
    if len(procedures) > 1:
        disclaimer = (
            "\n\nหมายเหตุ: เนื่องจากคุณทำหัตถการหลายอย่างร่วมกัน "
            "คำแนะนำบางอย่างอาจต้องปรับตามดุลยพินิจของทันตแพทย์ "
            "หากไม่แน่ใจ กรุณาสอบถามทีมแพทย์ที่ดูแลคุณโดยตรงนะคะ"
        )
        final_answer += disclaimer
        logger.info(f"Multi-procedure disclaimer appended (procedures: {procedures})")

    return {
        "answer": final_answer,
        "source": source,
        "used_chunks": used_chunks
    }

if __name__ == "__main__":
    result = asyncio.run(answer_patient_question(
        "ภาวะแทรกซ้อนที่เกิดจากการผ่าฟันคุด เกิดจากปัจจัยไรบ้าง", 
        {}
    ))
    
    print(result["answer"])
    print("\n\n")
    print("====================================================================")
    print(result["source"])
    print("\n\n")
    print("====================================================================")
    print(result["used_chunks"])
