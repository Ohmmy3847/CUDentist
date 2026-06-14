"""
Supabase Storage service for RAG documents.
Handles upload, download, list, and delete operations.

Storage keys are URL-encoded (Supabase rejects Thai chars and spaces).
Original filenames are preserved locally and in the manifest.
"""
import hashlib
import re
from pathlib import Path
from urllib.parse import unquote

from supabase import create_client, Client

from app.core.config import settings


def _client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def _safe_key(filename: str) -> str:
    """Convert filename to a unique Supabase-safe storage key (ASCII only, no spaces).

    If the original name contains non-ASCII characters (e.g. Thai), a short MD5
    hash of the full original name is appended so that two files with the same
    ASCII prefix but different Thai content never collide.
    """
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    ascii_stem = stem.encode("ascii", "ignore").decode()
    safe_stem = re.sub(r"[^\w\-]", "_", ascii_stem).strip("_")

    has_non_ascii = ascii_stem != stem
    if has_non_ascii:
        h = hashlib.md5(filename.encode()).hexdigest()[:8]
        return f"{safe_stem}_{h}{suffix}" if safe_stem else f"{h}{suffix}"

    if not safe_stem:
        safe_stem = hashlib.md5(filename.encode()).hexdigest()[:16]
    return f"{safe_stem}{suffix}"


def _original_name_from_metadata(storage_item: dict) -> str:
    """Extract original filename from storage item metadata, fall back to key."""
    meta = (storage_item.get("metadata") or {})
    return meta.get("original_name") or unquote(storage_item.get("name", ""))


def upload_file(filename: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Upload file to Supabase Storage. Returns the storage key used."""
    client = _client()
    bucket = settings.SUPABASE_STORAGE_BUCKET
    key = _safe_key(filename)
    client.storage.from_(bucket).upload(
        path=key,
        file=data,
        file_options={
            "content-type": content_type,
            "upsert": "true",
            "x-upsert": "true",
        },
    )
    return key


def download_file(filename: str) -> bytes:
    """Download file by original filename or storage key."""
    client = _client()
    key = _safe_key(filename)
    return client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).download(key)


def delete_file(filename: str) -> None:
    """Delete file by original filename or storage key."""
    client = _client()
    key = _safe_key(filename)
    client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).remove([key])


def list_files() -> list[dict]:
    """List all files. Returns items with 'name' = original filename where possible."""
    client = _client()
    return client.storage.from_(settings.SUPABASE_STORAGE_BUCKET).list()


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_to_temp(filename: str, tmp_dir: Path) -> Path:
    """Download file from Supabase Storage to a local directory. Returns local path."""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    dest = tmp_dir / filename
    dest.write_bytes(download_file(filename))
    return dest
