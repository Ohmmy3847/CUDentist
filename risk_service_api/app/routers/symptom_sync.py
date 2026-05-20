from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.symptom.mapping import get_collection
from app.core.factory import ModelFactory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/symptoms", tags=["symptoms"])

class SymptomSyncPayload(BaseModel):
    symptom_id: int
    symptom_name: str
    aliases: list[str] = []
    risk_level: Optional[str] = "ความเสี่ยงต่ำ"
    recommendation: Optional[str] = ""
    management: Optional[str] = ""
    action: str = "upsert"  # upsert | delete


def _process_sync(payload: SymptomSyncPayload):
    try:
        col = get_collection()
        sid = str(payload.symptom_id)

        # Always delete all existing entries for this symptom (canonical + aliases)
        try:
            col.delete(where={"symptom_id": sid})
        except Exception:
            pass

        if payload.action == "delete":
            logger.info(f"Deleted all entries for symptom {sid}")
            return

        # Embed all names: canonical + aliases
        embedding_function = ModelFactory.get_embeddings(use_case="symptom")
        all_names = [payload.symptom_name] + [a for a in (payload.aliases or []) if a.strip()]

        metadata = {
            "symptom_id": sid,
            "Risk level": payload.risk_level or "",
            "Recommendation": payload.recommendation or "",
            "Management": payload.management or "",
        }

        for i, name in enumerate(all_names):
            vec = embedding_function.embed_query(name)
            col.upsert(
                embeddings=[vec],
                documents=[name],
                ids=[f"s{sid}_{i}"],
                metadatas=[metadata],
            )
        logger.info(f"Upserted symptom {sid} with {len(all_names)} name(s)")

    except Exception as e:
        logger.error(f"Error syncing symptom to ChromaDB: {e}")
        raise

@router.post("/sync")
async def sync_symptom(payload: SymptomSyncPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(_process_sync, payload)
    return {"status": "accepted", "action": payload.action, "symptom_id": payload.symptom_id}


class RebuildPayload(BaseModel):
    symptoms: list[SymptomSyncPayload]


@router.post("/rebuild")
async def rebuild_symptoms(body: RebuildPayload, background_tasks: BackgroundTasks):
    """Delete entire 'symptoms' collection and rebuild from the provided list."""
    def _rebuild(symptoms: list[SymptomSyncPayload]):
        try:
            from app.services.rag.chunker import _get_chroma_client
            import chromadb as _chroma
            from chromadb.errors import NotFoundError

            client = _get_chroma_client()
            try:
                client.delete_collection("symptoms")
                logger.info("Deleted old 'symptoms' collection.")
            except (ValueError, NotFoundError):
                pass

            col = _get_chroma_client().get_or_create_collection("symptoms", metadata={"hnsw:space": "cosine"})
            embedding_function = ModelFactory.get_embeddings(use_case="symptom")

            for s in symptoms:
                vec = embedding_function.embed_query(s.symptom_name)
                col.upsert(
                    embeddings=[vec],
                    documents=[s.symptom_name],
                    ids=[str(s.symptom_id)],
                    metadatas={
                        "Risk level": s.risk_level or "",
                        "Recommendation": s.recommendation or "",
                        "Management": s.management or "",
                    },
                )
            logger.info(f"Rebuilt 'symptoms' collection with {len(symptoms)} entries.")
        except Exception as e:
            logger.error(f"Symptom rebuild failed: {e}")
            raise

    background_tasks.add_task(_rebuild, body.symptoms)
    return {"status": "accepted", "count": len(body.symptoms)}
