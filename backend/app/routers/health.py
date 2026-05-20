from fastapi import APIRouter, Request


router = APIRouter(tags=["health"])


@router.get("/health")
async def health(request: Request):
    engine = getattr(request.app.state, "db_engine", None)
    return {
        "status": "ok",
        "db_engine": "ready" if engine is not None else "missing",
    }

