import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.core.config import settings
from app.routers import assessment, logs, symptom_sync, documents as rag_documents
from app.services.risk.risk_service import build_llm
from app.services.rag.chunker import read_status, write_status

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _normalize_base_path(base_path: str) -> str:
    base_path = (base_path or "").strip()
    if base_path in {"", "/"}:
        return ""
    if not base_path.startswith("/"):
        base_path = f"/{base_path}"
    return base_path.rstrip("/")


API_BASE_PATH = _normalize_base_path(getattr(settings, "API_BASE_PATH", "/risk_service_api"))

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        docs_url=f"{API_BASE_PATH}/docs" if API_BASE_PATH else "/docs",
        redoc_url=f"{API_BASE_PATH}/redoc" if API_BASE_PATH else "/redoc",
        openapi_url=f"{API_BASE_PATH}/openapi.json" if API_BASE_PATH else "/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=getattr(settings, "ALLOW_ORIGIN_REGEX", r"https://.*\.vercel\.app"),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        app.state.llm = build_llm(settings.DEEPSEEK_API_KEY, settings.MODEL_NAME_DEFAULT)
        logger.info(f"✓ LLM initialized with model: {settings.MODEL_NAME_DEFAULT}")
        if read_status().get("status") == "error":
            write_status("idle")

    app.include_router(assessment.router, prefix=API_BASE_PATH)
    app.include_router(logs.router, prefix=API_BASE_PATH)
    app.include_router(symptom_sync.router, prefix=API_BASE_PATH)
    app.include_router(rag_documents.router, prefix=API_BASE_PATH)

    @app.get("/")
    async def service_root():
        return {
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "base_path": API_BASE_PATH or "/",
            "docs": f"{API_BASE_PATH}/docs" if API_BASE_PATH else "/docs",
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
