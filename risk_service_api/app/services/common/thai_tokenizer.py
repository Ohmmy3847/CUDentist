"""Thai tokenizer for BM25 sparse retrieval."""
from typing import List
from pythainlp.tokenize import word_tokenize as _thai_tokenize


def bm25_thai_preprocess(text: str) -> List[str]:
    """Thai-aware tokenizer for BM25 (newmm engine)."""
    return _thai_tokenize(text, engine="newmm")
