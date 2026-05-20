import shutil
from pathlib import Path

service_root = Path(__file__).resolve().parents[1]
chroma_dir = service_root / "data" / "chroma_db"

if chroma_dir.exists():
    print(f"Deleting entire ChromaDB directory: {chroma_dir}")
    shutil.rmtree(chroma_dir)
    print("Deleted successfully. You will need to re-run BOTH symptom ingestion and rag ingestion.")
else:
    print(f"Directory {chroma_dir} does not exist.")
