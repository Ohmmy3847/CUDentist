from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
import asyncio
from typing import List, Dict, Any


from app.core.constants import (
    FIELD_LABELS,
    FORM_COLUMNS,   
    FIELD_WITH_DESCRIPTION,
    DESCRIPTION_LABELS,
    CUSTOM_TEXT_FIELDS,
    PHONE_NUMBER
)


def map_symptom_to_predefined_symptom(symptom: str, llm) -> str:
    prompt = f"""
    You are a helpful assistant that maps user-input symptoms to predefined symptom labels.
    The predefined symptom labels are: {", ".join(DESCRIPTION_LABELS)}.
    If the user-input symptom does not match any predefined label, return "Other".
    
    User-input symptom: {symptom}
    """