"""
Together AI Embeddings Wrapper
==============================
OpenAI-compatible API wrapper for Together AI embedding models.
Same interface as OpenRouterEmbeddings but uses Together AI endpoint.
Pricing: ~$0.008/1M tokens (much cheaper than OpenRouter).
"""
import logging
import os
import time
from typing import List

import requests

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE = 100
MAX_CONCURRENT_EMBED = 4


class TogetherEmbeddings:
    """Wrapper for Together AI embedding models with batch support."""

    def __init__(self, model: str = "BAAI/bge-m3"):
        self.model = model
        self.api_key = os.getenv("TOGETHER_API_KEY", "")
        if not self.api_key:
            logger.warning("TOGETHER_API_KEY is not set. Embeddings might fail.")

    def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url="https://api.together.xyz/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": texts,
                    },
                    timeout=90,
                )
                response.raise_for_status()
                data = response.json()["data"]
                data.sort(key=lambda x: x["index"])
                return [d["embedding"] for d in data]

            except Exception as e:
                logger.error(f"Together embedding error (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logger.info(f"Retrying embedding batch in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error("Max retries reached. Returning zero embeddings.")
                    return [[0.0] * 1024 for _ in texts]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        total_batches = (len(texts) + EMBED_BATCH_SIZE - 1) // EMBED_BATCH_SIZE

        batches = [
            (i // EMBED_BATCH_SIZE, texts[i : i + EMBED_BATCH_SIZE])
            for i in range(0, len(texts), EMBED_BATCH_SIZE)
        ]

        results: dict[int, List[List[float]]] = {}
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_EMBED) as executor:
            futures = {
                executor.submit(self._get_embeddings_batch, batch): idx
                for idx, batch in batches
            }
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()

        all_embeddings: List[List[float]] = []
        for i in range(total_batches):
            all_embeddings.extend(results[i])
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        return self._get_embeddings_batch([text])[0]
