"""
Document management + ingest trigger endpoints for risk_service_api.
These are internal endpoints (no auth) — called via backend proxy.
"""
import asyncio
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
    save_manifest,
    read_status,
)
from app.services.storage_service import (
    upload_file,
    delete_file,
    list_files,
    sha256_of_bytes,
)

router = APIRouter(prefix="/documents", tags=["rag-documents"])

ALLOWED_EXTENSIONS = SUPPORTED_EXTENSIONS  # {".pdf", ".txt", ".md", ".docx"}
MAX_SIZE = 50 * 1024 * 1024  # 50 MB


@router.get("", summary="List documents in Supabase Storage")
async def list_documents():
    manifest = load_manifest()
    try:
        storage_files = list_files()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Storage error: {e}")

    from app.services.rag.chunker import MANIFEST_STORAGE_KEY
    result = []
    for f in storage_files:
        key = f.get("name", "")
        if key == MANIFEST_STORAGE_KEY:
            continue  # skip the internal manifest file
        ext = Path(key).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        info = manifest.get(key, {})
        metadata = f.get("metadata") or {}
        display_name = info.get("original_name") or key
        result.append({
            "filename": display_name,
            "storage_key": key,
            "size": metadata.get("size", 0),
            "extension": ext,
            "sha256": info.get("sha256"),
            "last_ingested": info.get("last_ingested"),
            "is_indexed": bool(info.get("last_ingested")),
        })
    return sorted(result, key=lambda x: x["filename"].lower())


@router.post("", status_code=status.HTTP_201_CREATED, summary="Upload a document to Supabase Storage")
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

    # Check for duplicate by sha256 against manifest
    new_hash = sha256_of_bytes(data)
    manifest = load_manifest()
    for existing_name, info in manifest.items():
        if info.get("sha256") == new_hash:
            return {"filename": existing_name, "size": len(data), "status": "already_exists"}

    try:
        key = upload_file(file.filename, data, file.content_type or "application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Storage upload failed: {e}")

    # Persist original filename so the list endpoint can display it
    manifest = load_manifest()
    entry = manifest.get(key, {})
    entry["original_name"] = file.filename
    manifest[key] = entry
    save_manifest(manifest)

    return {"filename": file.filename, "storage_key": key, "size": len(data), "status": "uploaded"}


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

    # Remove from Supabase Storage
    try:
        delete_file(filename)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Also remove local cache if exists
    local = DOCUMENT_DIR / filename
    if local.exists():
        local.unlink(missing_ok=True)

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
