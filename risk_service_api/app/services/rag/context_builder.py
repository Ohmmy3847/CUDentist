"""
Context Builder for RAG Pipeline
─────────────────────────────────
Builds a rich patient context from assessment data for the RAG pipeline.
"""
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Symptom fields to extract from assessment_data
SYMPTOM_FIELDS = {
    "pain_score":           "ระดับปวด",
    "pain_medication_effect": "ผลยาแก้ปวด",
    "pain_description":     "รายละเอียดปวด",
    "swelling_status":      "อาการบวม",
    "swelling_description": "รายละเอียดบวม",
    "breathing_or_swallowing_difficulty": "หายใจ/กลืน",
    "breathing_description": "รายละเอียดหายใจ",
    "bleeding_status":      "เลือดออก",
    "bleeding_description": "รายละเอียดเลือด",
    "fever_status":         "ไข้",
    "fever_description":    "รายละเอียดไข้",
    "numbness_status":      "อาการชา",
    "numbness_description": "รายละเอียดชา",
    "phlebitis":            "หลอดเลือดดำอักเสบ",
    "suture_status":        "ไหมละลาย",
}


def _calc_days_post_op(surgery_date_str: Optional[str]) -> Optional[int]:
    """Calculate days since surgery."""
    if not surgery_date_str:
        return None
    try:
        surgery_date = datetime.strptime(surgery_date_str, "%Y-%m-%d").date()
        return (date.today() - surgery_date).days
    except (ValueError, TypeError):
        return None


def _build_patient_profile(basic_info: dict) -> dict:
    """Extract relevant patient profile from basic_info."""
    profile = {}

    # Procedures
    procedures = basic_info.get("procedures", [])
    if procedures:
        profile["procedures"] = procedures

    # Sub-options
    for key in ("lefort_sub_options", "bssro_sub_options"):
        val = basic_info.get(key)
        if val:
            profile[key] = val

    # Days post-op
    days = _calc_days_post_op(basic_info.get("surgery_date"))
    if days is not None:
        profile["days_post_op"] = days
        profile["surgery_date"] = basic_info["surgery_date"]

    # IMF / Special
    if basic_info.get("imf_wire"):
        profile["imf_wire"] = True
        loops = basic_info.get("imf_wire_loops")
        if loops:
            profile["imf_wire_loops"] = loops
    if basic_info.get("imf_elastic"):
        profile["imf_elastic"] = True
        loops = basic_info.get("imf_elastic_loops")
        if loops:
            profile["imf_elastic_loops"] = loops
    if basic_info.get("special_icbg"):
        profile["special_icbg"] = True
    if basic_info.get("special_ng_tube"):
        profile["special_ng_tube"] = True

    # Patient note (allergies, special conditions from nurse)
    patient_note = basic_info.get("patient_note")
    if patient_note:
        profile["patient_note"] = patient_note

    return profile


def _build_current_symptoms(assessment_data: dict) -> dict:
    """Extract current symptoms from assessment_data (English keys, Thai/raw values)."""
    symptoms = {}
    for field in SYMPTOM_FIELDS:
        val = assessment_data.get(field)
        if val and str(val).strip() and str(val).strip() != "":
            symptoms[field] = val

    # Other symptoms
    other = assessment_data.get("other_symptoms", [])
    if other:
        symptoms["other_symptoms"] = other

    # Care info
    for key in [
        "antibiotic_compliance",
        "compress_type",
        "imf_wire_status",
        "brushing_teeth",
        "mouth_rinsing",
        "food_types",
        "food_amount",
    ]:
        val = assessment_data.get(key)
        if val and str(val).strip():
            symptoms[key] = val

    return symptoms


def _build_risk_assessment(flows: dict, summary: dict) -> dict:
    """Extract risk assessment from flows and summary."""
    assessment = {
        "overall_risk": summary.get("overall_risk", "ไม่ระบุ"),
    }

    # Per-flow risks (only include those with actual risk or recommendations)
    flow_risks = {}
    for flow_name, flow_data in flows.items():
        if not isinstance(flow_data, dict):
            continue
        risk = flow_data.get("risk_level", "")
        if risk in ("ไม่ต้องประเมิน",):
            continue
        entry = {"risk_level": risk}
        reason = flow_data.get("reason", "")
        if reason:
            entry["reason"] = reason
        rec = flow_data.get("recommendation", "")
        if rec:
            entry["recommendation"] = rec
        flow_risks[flow_name] = entry

    assessment["flows"] = flow_risks

    # Active recommendations
    recommendations = []
    for flow_name, flow_data in flows.items():
        if isinstance(flow_data, dict):
            rec = flow_data.get("recommendation", "")
            if rec:
                recommendations.append(f"{flow_name}: {rec}")
    if recommendations:
        assessment["recommendations"] = recommendations

    return assessment


def build_patient_context(
    basic_info: dict,
    assessment_data: dict,
    flows: dict,
    summary: dict,
) -> dict:
    """
    Build a rich patient context for the RAG pipeline.

    Returns a structured dict with:
    - patient_profile: procedures, days_post_op, IMF, etc.
    - current_symptoms: all current symptom statuses
    - risk_assessment: overall + per-flow risk with recommendations
    """
    context = {
        "patient_profile": _build_patient_profile(basic_info),
        "current_symptoms": _build_current_symptoms(assessment_data),
        "risk_assessment": _build_risk_assessment(flows, summary),
    }

    logger.info(
        f"Built patient context: "
        f"{len(context['patient_profile'])} profile fields, "
        f"{len(context['current_symptoms'])} symptoms, "
        f"{len(context['risk_assessment'].get('flows', {}))} flow risks"
    )

    return context
