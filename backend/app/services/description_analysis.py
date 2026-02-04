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
