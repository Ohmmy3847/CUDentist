from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv

from app.core.config import settings
from app.routers import classification, logs
from app.services.risk_service import build_llm

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
# Initialize LLM
llm = build_llm(settings.GOOGLE_API_KEY, settings.MODEL_NAME)
logger.info(f"Initialized LLM with model: {settings.MODEL_NAME}")


# Dependency for LLM injection
def get_llm():
    """Dependency to inject LLM into endpoints"""
    return llm


# Make get_llm available to routers
classification.get_llm = get_llm

# Include routers
app.include_router(classification.router)
app.include_router(logs.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
