"""Thai tokenizer for BM25 sparse retrieval."""
from typing import List
from pythainlp.tokenize import word_tokenize as _thai_tokenize


def bm25_thai_preprocess(text: str) -> List[str]:
    """Thai-aware tokenizer for BM25 (newmm engine).

    Strips whitespace-only tokens that newmm emits for spaces between
    mixed Thai-English text — they add noise to BM25 scoring.
    """
    tokens = _thai_tokenize(text, engine="newmm", keep_whitespace=False)
    return [t for t in tokens if t.strip()]
