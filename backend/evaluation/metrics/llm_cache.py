"""
LLM Cache for faster metric evaluation
Reuse LLM instances across metrics
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from functools import lru_cache


@lru_cache(maxsize=10)
def get_llm(model: str = "gemini-2.5-flash", temperature: float = 0, timeout: int = 60 ):
    """
    Get cached LLM instance
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
        timeout=timeout,
        max_tokens=8192
    )
