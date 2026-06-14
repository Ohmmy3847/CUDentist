import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    API_TITLE: str = os.getenv("API_TITLE", "Website Backend API")
    API_VERSION: str = os.getenv("API_VERSION", "0.1.0")

    API_BASE_PATH: str = os.getenv("API_BASE_PATH", "/backend")

    PORT: int = int(os.getenv("PORT", "8001"))
    RELOAD: bool = os.getenv("RELOAD", "false").lower() in {"1", "true", "yes", "y"}

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/app",
    )

    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    ALLOW_ORIGIN_REGEX: str | None = os.getenv("ALLOW_ORIGIN_REGEX", r"https://.*\.(vercel\.app|trycloudflare\.com)")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-please-use-a-long-random-string")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    RISK_SERVICE_URL: str = os.getenv("RISK_SERVICE_URL", "http://localhost:8000")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    FORM_TOKEN_EXPIRE_DAYS: int = int(os.getenv("FORM_TOKEN_EXPIRE_DAYS", "7"))

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() in {"1", "true", "yes"}
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@example.com")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")

    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    LINE_CHANNEL_SECRET: str = os.getenv("LINE_CHANNEL_SECRET", "")
    # How many hours before/after schedule time to still attempt sending (catch-up window)
    LINE_SEND_WINDOW_HOURS: int = int(os.getenv("LINE_SEND_WINDOW_HOURS", "2"))

    # Supabase Storage (for RAG documents)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "documents")


settings = Settings()
