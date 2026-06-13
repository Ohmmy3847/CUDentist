"""
Document management + ingest trigger endpoints for risk_service_api.
These are internal endpoints (no auth) — called via backend proxy.
"""
import asyncio
import hashlib
import shutil
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, status
from pydantic import BaseModel

from app.services.rag.chunker import (
    DOCUMENT_DIR,
    CHROMADB_DIR,
    COLLECTION_NAME,
    SUPPORTED_EXTENSIONS,
    ingest,
    load_manifest,
    read_status,
)

router = APIRouter(prefix="/documents", tags=["rag-documents"])

ALLOWED_EXTENSIONS = SUPPORTED_EXTENSIONS  # {".pdf", ".txt", ".md", ".docx"}
MAX_SIZE = 50 * 1024 * 1024  # 50 MB


def _list_doc_files() -> list[Path]:
    files = []
    for ext in ALLOWED_EXTENSIONS:
        files.extend(DOCUMENT_DIR.rglob(f"*{ext}"))
    return sorted(files, key=lambda f: f.name.lower())


@router.get("", summary="List documents in the RAG document directory")
async def list_documents():
    manifest = load_manifest()
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
    files = _list_doc_files()
    result = []
    for f in files:
        info = manifest.get(f.name, {})
        result.append({
            "filename": f.name,
            "size": f.stat().st_size,
            "extension": f.suffix.lower(),
            "relative_path": str(f.relative_to(DOCUMENT_DIR)),
            "sha256": info.get("sha256"),
            "last_ingested": info.get("last_ingested"),
            "is_indexed": f.name in manifest,
        })
    return result


@router.post("", status_code=status.HTTP_201_CREATED, summary="Upload a document to RAG directory")
async def upload_document(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds 50 MB limit")

    # Save to DOCUMENT_DIR root (flat structure for uploaded files)
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
    dest = DOCUMENT_DIR / file.filename
    # Deduplicate: if file exists with same content, skip; else add _1 _2 suffix
    if dest.exists():
        existing_hash = hashlib.sha256(dest.read_bytes()).hexdigest()
        new_hash = hashlib.sha256(data).hexdigest()
        if existing_hash == new_hash:
            return {"filename": file.filename, "size": len(data), "status": "already_exists"}
        # Different content: add suffix
        stem = dest.stem
        suffix = dest.suffix
        counter = 1
        while dest.exists():
            dest = DOCUMENT_DIR / f"{stem}_{counter}{suffix}"
            counter += 1

    dest.write_bytes(data)
    return {"filename": dest.name, "size": len(data), "status": "uploaded"}


# ---------------------------------------------------------------------------
# POST /ask  — test RAG Q&A without patient context
# (must be defined before /{filename} to avoid wildcard collision)
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    question: str


@router.post("/ask", summary="Test RAG Q&A (no patient context)")
async def ask_rag(body: AskRequest):
    from app.services.rag.pipeline import answer_patient_question
    result = await answer_patient_question(
        question=body.question.strip(),
        patient_context={},
    )
    return result


@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document and its ChromaDB chunks")
async def delete_document(filename: str):
    # Prevent path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

    # Find the file (search recursively since docs may be in subdirectories)
    target = None
    for f in _list_doc_files():
        if f.name == filename:
            target = f
            break

    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Remove from disk
    target.unlink(missing_ok=True)

    # Remove from ChromaDB
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMADB_DIR))
        try:
            col = client.get_collection(COLLECTION_NAME)
            col.delete(where={"source": filename})
        except Exception:
            pass
    except Exception:
        pass

    # Remove from manifest
    try:
        from app.services.rag.chunker import load_manifest, save_manifest
        manifest = load_manifest()
        if filename in manifest:
            del manifest[filename]
            save_manifest(manifest)
    except Exception:
        pass


class TextDocumentRequest(BaseModel):
    filename: str
    content: str


class TextDocumentUpdateRequest(BaseModel):
    content: str


@router.post("/text", status_code=status.HTTP_201_CREATED, summary="Create a new text document")
async def create_text_document(body: TextDocumentRequest):
    name = body.filename.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="filename is required")
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
    if not name.endswith(".txt"):
        name = name + ".txt"
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
    dest = DOCUMENT_DIR / name
    if dest.exists():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="File already exists")
    dest.write_text(body.content, encoding="utf-8")
    return {"filename": dest.name, "size": dest.stat().st_size, "status": "created"}


@router.get("/text/{filename}", summary="Get text document content")
async def get_text_document(filename: str):
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
    target = DOCUMENT_DIR / filename
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if target.suffix.lower() not in (".txt", ".md"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .txt and .md files are editable")
    return {"filename": filename, "content": target.read_text(encoding="utf-8")}


@router.put("/text/{filename}", summary="Update text document content")
async def update_text_document(filename: str, body: TextDocumentUpdateRequest):
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
    target = DOCUMENT_DIR / filename
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if target.suffix.lower() not in (".txt", ".md"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .txt and .md files are editable")
    target.write_text(body.content, encoding="utf-8")
    return {"filename": filename, "size": target.stat().st_size, "status": "updated"}


class IngestRequest(BaseModel):
    mode: str = "append"  # "reingest" | "append"


_ingest_lock = asyncio.Lock()


@router.post("/ingest", summary="Trigger document ingestion into ChromaDB")
async def trigger_ingest(body: IngestRequest, background_tasks: BackgroundTasks):
    if body.mode not in ("reingest", "append"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mode must be 'reingest' or 'append'")

    status_data = read_status()
    if status_data.get("status") == "running":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ingestion already in progress")

    background_tasks.add_task(ingest, mode=body.mode)
    return {"started": True, "mode": body.mode}


@router.get("/ingest/status", summary="Get current ingest status")
async def ingest_status():
    return read_status()
