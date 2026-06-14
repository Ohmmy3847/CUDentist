"""
Application Configuration and Settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "Risk Classification API"
    API_VERSION: str = "1.0.0"
    API_BASE_PATH: str = os.getenv("API_BASE_PATH", "/risk_service_api")
    
    # API Keys & Providers
    LLM_PROVIDER_DEFAULT: str = os.getenv("LLM_PROVIDER_DEFAULT", "deepseek")
    LLM_PROVIDER_RAG: str = os.getenv("LLM_PROVIDER_RAG", "deepseek")
    LLM_PROVIDER_SUMMARY: str = os.getenv("LLM_PROVIDER_SUMMARY", "deepseek")
    LLM_PROVIDER_SYMPTOM: str = os.getenv("LLM_PROVIDER_SYMPTOM", "deepseek")
    
    EMBEDDING_PROVIDER_DEFAULT: str = os.getenv("EMBEDDING_PROVIDER_DEFAULT", "openrouter")
    EMBEDDING_PROVIDER_RAG: str = os.getenv("EMBEDDING_PROVIDER_RAG", "openrouter")
    EMBEDDING_PROVIDER_SYMPTOM: str = os.getenv("EMBEDDING_PROVIDER_SYMPTOM", "openrouter")

    EMBEDDING_MODEL_RAG: str = os.getenv("EMBEDDING_MODEL_RAG", "qwen/qwen3-embedding-8b")
    EMBEDDING_MODEL_SYMPTOM: str = os.getenv("EMBEDDING_MODEL_SYMPTOM", "qwen/qwen3-embedding-8b")
    
    # Keys for various providers
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPEN_ROUTER_API_KEY: str = os.getenv("OPEN_ROUTER_API_KEY", "")
    TOGETHER_API_KEY: str = os.getenv("TOGETHER_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    MODEL_NAME_DEFAULT: str = os.getenv("MODEL_NAME_DEFAULT", "deepseek-chat")
    MODEL_NAME_RAG: str = os.getenv("MODEL_NAME_RAG", "deepseek-chat")
    MODEL_NAME_SUMMARY: str = os.getenv("MODEL_NAME_SUMMARY", "deepseek-chat")
    MODEL_NAME_SYMPTOM: str = os.getenv("MODEL_NAME_SYMPTOM", "deepseek-chat")
    
    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "https://cudent.vercel.app",
    ]
    ALLOW_ORIGIN_REGEX: str = r"https://.*\.vercel\.app"
    
    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # ChromaDB
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8002"))

    # Supabase Storage
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "documents")
    
    # CSV Processing
    MAX_CONCURRENT_REQUESTS: int = 10
    
    def __init__(self):
        """Initialize settings and validate"""
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        # Add FRONTEND_URL to allowed origins if specified
        if self.FRONTEND_URL and self.FRONTEND_URL not in self.ALLOWED_ORIGINS:
            self.ALLOWED_ORIGINS.append(self.FRONTEND_URL)
        
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)



# Global settings instance
settings = Settings()
