"""
Dependency injection functions for FastAPI
"""
from fastapi import Request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


def get_llm(request: Request) -> "ChatOpenAI":
    """
    Dependency to inject LLM into endpoints.
    LLM is initialized once during startup and stored in app.state.
    """
    return request.app.state.llm
