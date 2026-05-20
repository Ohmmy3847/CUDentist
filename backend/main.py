import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text, update

from app.core.config import settings
from app.core.db import create_engine, create_session_factory
from app.models.form_token import FormToken
from app.models.patient import Patient
from app.routers import (
    health_router,
    auth_router,
    patients_router,
    assessments_router,
    symptoms_router,
    dashboard_router,
    public_form_router,
    line_webhook_router,
    rag_admin_router,
)
from app.services.line_service import push_form_link

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

API_BASE_PATH = settings.API_BASE_PATH


async def _line_scheduler(session_factory) -> None:
    """Runs every minute. Pushes form links for schedules that are now due."""
    # Prevent duplicate sends when running multiple app processes (e.g. uvicorn --reload),
    # by taking a Postgres advisory lock. If we can't get the lock, we skip this tick.
    advisory_lock_key = 921_337_001
    while True:
        await asyncio.sleep(60)
        try:
            async with session_factory() as session:
                locked = await session.scalar(
                    text("SELECT pg_try_advisory_lock(:key)"),
                    {"key": advisory_lock_key},
                )
                if not locked:
                    continue
                try:
                    now = datetime.now(timezone.utc)
                    window = timedelta(hours=settings.LINE_SEND_WINDOW_HOURS)
                    result = await session.execute(
                        select(FormToken).where(
                            FormToken.line_sent == False,  # noqa: E712
                            FormToken.is_used == False,  # noqa: E712
                            FormToken.schedule_date.isnot(None),
                            FormToken.expires_at > now,
                        )
                    )
                    tokens = result.scalars().all()
                    for token in tokens:
                        try:
                            sched = datetime.fromisoformat(
                                token.schedule_date.replace("Z", "+00:00")
                            )
                        except Exception:
                            continue
                        if not (now - window <= sched <= now + window):
                            continue
                        patient = await session.get(Patient, token.patient_hn)
                        if not patient or not patient.line_user_id:
                            continue
                        try:
                            url = f"{settings.FRONTEND_URL}/form/{token.token}"
                            plain_password = token.token[:6]
                            await push_form_link(
                                patient.line_user_id,
                                patient.first_name,
                                url,
                                plain_password,
                            )
                            await session.execute(
                                update(FormToken)
                                .where(FormToken.token == token.token)
                                .values(line_sent=True)
                            )
                            await session.commit()
                            logger.info("LINE form link sent to patient %s", token.patient_hn)
                        except Exception as exc:
                            logger.error("Failed LINE push to patient %s: %s", token.patient_hn, exc)
                finally:
                    await session.execute(
                        text("SELECT pg_advisory_unlock(:key)"),
                        {"key": advisory_lock_key},
                    )
        except Exception as exc:
            logger.error("Line scheduler error: %s", exc)


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_engine(settings.DATABASE_URL)
        session_factory = create_session_factory(engine)
        app.state.db_engine = engine
        app.state.session_factory = session_factory
        app.state.line_scheduler_task = asyncio.create_task(
            _line_scheduler(session_factory)
        )
        logger.info("✓ DB engine + LINE scheduler started")
        yield
        task = getattr(app.state, "line_scheduler_task", None)
        if task:
            task.cancel()
        engine = getattr(app.state, "db_engine", None)
        if engine is not None:
            await engine.dispose()
            logger.info("✓ DB engine disposed")

    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=settings.ALLOW_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = API_BASE_PATH

    app.include_router(health_router, prefix=prefix)
    app.include_router(auth_router, prefix=prefix)
    app.include_router(patients_router, prefix=prefix)
    app.include_router(assessments_router, prefix=prefix)
    app.include_router(symptoms_router, prefix=prefix)
    app.include_router(dashboard_router, prefix=prefix)
    app.include_router(public_form_router, prefix=prefix)
    app.include_router(line_webhook_router, prefix=prefix)
    app.include_router(rag_admin_router, prefix=prefix)

    @app.get("/")
    async def service_root():
        return {
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "docs": f"{prefix}/docs",
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.RELOAD)
