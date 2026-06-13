import logging

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.deps import get_current_user, require_permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag-admin"])

_RAG_PREFIX = "/risk_service_api"


def _rag_url(path: str) -> str:
    base = settings.RISK_SERVICE_URL.rstrip("/")
    return f"{base}{_RAG_PREFIX}{path}"


# ---------------------------------------------------------------------------
# GET /rag/documents  — list RAG documents (any authenticated user)
# ---------------------------------------------------------------------------
@router.get("/documents")
async def list_rag_documents(_=Depends(get_current_user)):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(_rag_url("/documents"))
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")


# ---------------------------------------------------------------------------
# POST /rag/documents  — upload file to RAG service (manage_docs)
# ---------------------------------------------------------------------------
@router.post("/documents", status_code=status.HTTP_201_CREATED)
async def upload_rag_document(
    file: UploadFile = File(...),
    _=Depends(require_permission("manage_docs")),
):
    try:
        data = await file.read()
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                _rag_url("/documents"),
                files={"file": (file.filename, data, file.content_type or "application/octet-stream")},
            )
            resp.raise_for_status()
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")


# ---------------------------------------------------------------------------
# DELETE /rag/documents/{filename}  — delete file + ChromaDB chunks (manage_docs)
# ---------------------------------------------------------------------------
@router.delete("/documents/{filename}")
async def delete_rag_document(
    filename: str,
    _=Depends(require_permission("manage_docs")),
):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.delete(_rag_url(f"/documents/{filename}"))
            resp.raise_for_status()
            return JSONResponse(status_code=resp.status_code, content=None)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")


# ---------------------------------------------------------------------------
# Text document CRUD  — create / read / update editable .txt documents
# ---------------------------------------------------------------------------
@router.post("/text-documents", status_code=status.HTTP_201_CREATED)
async def create_text_document(body: dict, _=Depends(require_permission("manage_docs"))):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(_rag_url("/documents/text"), json=body)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")


@router.get("/text-documents/{filename}")
async def get_text_document(filename: str, _=Depends(require_permission("manage_docs"))):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(_rag_url(f"/documents/text/{filename}"))
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")


@router.put("/text-documents/{filename}")
async def update_text_document(filename: str, body: dict, _=Depends(require_permission("manage_docs"))):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.put(_rag_url(f"/documents/text/{filename}"), json=body)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")


# ---------------------------------------------------------------------------
# POST /rag/ingest  — trigger ingest (manage_docs)
# ---------------------------------------------------------------------------
@router.post("/ingest")
async def trigger_ingest(
    body: dict,
    _=Depends(require_permission("manage_docs")),
):
    mode = body.get("mode")
    if mode not in ("reingest", "append"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mode must be 'reingest' or 'append'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(_rag_url("/documents/ingest"), json={"mode": mode})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")


# ---------------------------------------------------------------------------
# GET /rag/ingest/status  — get ingest status (any authenticated user)
# ---------------------------------------------------------------------------
@router.get("/ingest/status")
async def get_ingest_status(_=Depends(get_current_user)):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(_rag_url("/documents/ingest/status"))
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")


# ---------------------------------------------------------------------------
# POST /rag/ask  — test RAG Q&A without patient context (any authenticated user)
# ---------------------------------------------------------------------------
@router.post("/ask")
async def ask_rag(body: dict, _=Depends(get_current_user)):
    if not body.get("question", "").strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="question is required")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(_rag_url("/documents/ask"), json=body)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except httpx.RequestError as exc:
        logger.error("RAG service unreachable: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="RAG service unavailable")
