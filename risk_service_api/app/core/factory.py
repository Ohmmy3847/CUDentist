"""
Model & Embedding Factory
=========================
รับผิดชอบการสร้าง LLM และ Embedding object อิงจาก Environment Variables 
เพื่อให้สลับ Provider (DeepSeek, OpenAI, Gemini, Ollama) ได้โดยไม่ต้องแก้โค้ดที่อื่น
"""
import logging
from typing import Optional
from enum import Enum

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    TOGETHER = "together"


class EmbeddingProvider(str, Enum):
    OPENROUTER = "openrouter"
    TOGETHER = "together"
    OPENAI = "openai"
    OLLAMA = "ollama"


class ModelFactory:
    """Factory สำหรับ Get LLM และ Embedding Models"""

    @staticmethod
    def get_llm(
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.0,
        use_case: str = "default"  # "default", "rag", "summary", "symptom"
    ) -> BaseChatModel:
        """
        สร้าง ChatModel ตาม Provider ที่กำหนด หรือตามค่า Default ใน Settings ของแต่ละ Use Case
        """
        # 1. เลือก Provider โดย Fallback ไปหา _DEFAULT หากไม่ได้ตั้งค่าไว้
        if use_case == "rag":
            p_val = settings.LLM_PROVIDER_RAG
            m_val = settings.MODEL_NAME_RAG
        elif use_case == "summary":
            p_val = settings.LLM_PROVIDER_SUMMARY
            m_val = settings.MODEL_NAME_SUMMARY
        elif use_case == "symptom":
            p_val = settings.LLM_PROVIDER_SYMPTOM
            m_val = settings.MODEL_NAME_SYMPTOM
        else:
            p_val = settings.LLM_PROVIDER_DEFAULT
            m_val = settings.MODEL_NAME_DEFAULT

        # Fallback to default if explicitly passed parameter is None, 
        # and fallback to _DEFAULT config if the use_case specific config is missing or empty
        p = provider or p_val or settings.LLM_PROVIDER_DEFAULT
        m = model_name or m_val or settings.MODEL_NAME_DEFAULT
        
        p = p.lower()

        logger.debug(f"[ModelFactory] Initializing LLM => Use Case: {use_case}, Provider: {p}, Model: {m}")

        if p == ModelProvider.DEEPSEEK:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com" if not settings.DEEPSEEK_API_KEY.startswith("sk-or-") else "https://openrouter.ai/api/v1",
                model=m or "deepseek-chat",
                temperature=temperature,
                max_retries=3,
            )

        elif p == ModelProvider.OPENAI:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=m or "gpt-4o-mini",
                temperature=temperature,
                max_retries=3,
            )

        elif p == ModelProvider.GEMINI:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                google_api_key=settings.GOOGLE_API_KEY,
                model=m or "gemini-1.5-flash",
                temperature=temperature,
                max_retries=3,
            )
            
        elif p == ModelProvider.OLLAMA:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=m or "llama3",
                base_url=settings.OLLAMA_BASE_URL,
                temperature=temperature,
            )

        elif p == ModelProvider.OPENROUTER:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=settings.OPEN_ROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                model=m,
                temperature=temperature,
                max_retries=3,
            )

        elif p == ModelProvider.TOGETHER:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=settings.TOGETHER_API_KEY,
                base_url="https://api.together.xyz/v1",
                model=m or "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                temperature=temperature,
                max_retries=3,
            )

        else:
            raise ValueError(f"Unsupported LLM provider: {p}")


    @staticmethod
    def get_embeddings(
        provider: Optional[str] = None,
        use_case: str = "default"  # "default", "symptom", "rag"
    ) -> Embeddings:
        """
        สร้าง Embeddings Model ตาม Provider 
        """
        if use_case == "symptom":
            p_val = settings.EMBEDDING_PROVIDER_SYMPTOM
        elif use_case == "rag":
            p_val = settings.EMBEDDING_PROVIDER_RAG
        else:
            p_val = settings.EMBEDDING_PROVIDER_DEFAULT
            
        # Fallback to default if missing
        p = provider or p_val or settings.EMBEDDING_PROVIDER_DEFAULT
        p = p.lower()

        logger.debug(f"[ModelFactory] Initializing Embeddings => Use Case: {use_case}, Provider: {p}")

        if p == EmbeddingProvider.OPENROUTER:
            from app.services.rag.chunker import OpenRouterEmbeddings
            model = (
                settings.EMBEDDING_MODEL_SYMPTOM if use_case == "symptom"
                else settings.EMBEDDING_MODEL_RAG
            )
            return OpenRouterEmbeddings(model=model)

        elif p == EmbeddingProvider.TOGETHER:
            from app.services.common.together_embeddings import TogetherEmbeddings
            model = (
                settings.EMBEDDING_MODEL_SYMPTOM if use_case == "symptom"
                else settings.EMBEDDING_MODEL_RAG
            )
            return TogetherEmbeddings(model=model)

        elif p == EmbeddingProvider.OPENAI:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                api_key=settings.OPENAI_API_KEY,
                model="text-embedding-3-large"
            )

        elif p == EmbeddingProvider.OLLAMA:
            from langchain_ollama import OllamaEmbeddings
            return OllamaEmbeddings(
                model="nomic-embed-text",  # or custom model
                base_url=settings.OLLAMA_BASE_URL,
            )

        else:
            raise ValueError(f"Unsupported Embedding provider: {p}")
