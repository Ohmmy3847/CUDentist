"""
Risk Service - Core Functions

Entry point สำหรับ risk classification system:
- build_llm: สร้าง LLM instance
- classify_risk: Rule-based risk classification

Re-exports functions ที่ไฟล์อื่นใช้เพื่อ backward compatibility:
- summarize_all_risks, answer_patient_questions จาก summarizer.py
- FORM_COLUMNS, FIELD_LABELS จาก constants.py
"""
import logging
from typing import Dict, Optional

from pydantic import SecretStr
from app.core.factory import ModelFactory

from app.core.constants import FIELD_LABELS, FORM_COLUMNS, PHONE_NUMBER
from app.models.schemas import OutputRiskClassification
from app.services.risk.flow_parser import RuleEngine

# Re-exports for backward compatibility
from app.services.risk.summarizer import summarize_all_risks, answer_patient_questions  # noqa: F401

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# LLM Builder
# ------------------------------------------------------------

def build_llm(api_key: str, model_name: str = "deepseek-chat"):
    """Build LLM via Factory (Summary Use Case)"""
    return ModelFactory.get_llm(
        use_case="summary",
        model_name=model_name,
        temperature=0.1
    )


# ------------------------------------------------------------
# Main Risk Classification (Rule-Based)
# ------------------------------------------------------------

def classify_risk(input_data: dict, api_key: Optional[str] = None, flow: Optional[str] = None, flow_name: Optional[str] = None, llm=None, max_retries: int = 3, language: str = 'th'):
    """
    Classify risk using Rule Engine (deterministic)
    Args:
        input_data: Patient data dictionary
        api_key: Google API key (optional, kept for backward compatibility)
        flow: Risk flow criteria (kept for backward compatibility, not used)
        flow_name: Name of the flow to evaluate
        llm: Pre-built LLM instance (optional, kept for backward compatibility)
        max_retries: Maximum number of retries (kept for backward compatibility)
        language: Language for output ('th' or 'en')
    """
    engine = RuleEngine()
    
    try:
        # Use default flow name if not provided
        effective_flow_name = flow_name or "pregnancy_risk"
        result = engine.evaluate_flow(effective_flow_name, input_data, language=language)
        
        return OutputRiskClassification(
            risk_level=result.get('risk_level', 'ไม่สามารถประเมินได้'),
            recommendation=result.get('recommendation') or "",
            reason=result.get('reason') or ""
        )
        
    except Exception as e:
        print(f"Error in rule-based classification for {flow_name}: {str(e)}")
        
        return OutputRiskClassification(
            risk_level="ไม่สามารถประเมินได้" if language == 'th' else "Cannot assess",
            recommendation="กรุณาติดต่อทีมแพทย์เพื่อประเมินเพิ่มเติม" if language == 'th' else "Please contact medical team for further assessment",
            reason=f"ไม่สามารถประเมินได้: {str(e)[:100]}" if language == 'th' else f"Cannot assess: {str(e)[:100]}"
        )
