"""One place to get embeddings, so every example uses the same function.

Preferred : sentence-transformers 'all-MiniLM-L6-v2' (real semantic embeddings, 384 dims,
            downloads ~90 MB the first time).
Fallback  : a tiny hashed bag-of-words embedding. It only matches *shared words*, not
            meaning - fine for running the code offline, but NOT real semantic search.
"""
import hashlib
import numpy as np

DIM_FALLBACK = 256
_model = None
USING_REAL_MODEL = False


def _toy_embed(text: str) -> np.ndarray:
    v = np.zeros(DIM_FALLBACK, dtype="float32")
    for word in text.lower().replace(",", " ").replace(".", " ").replace("?", " ").split():
        h = int(hashlib.md5(word.encode()).hexdigest(), 16)
        v[h % DIM_FALLBACK] += 1.0
    n = np.linalg.norm(v)
    return v / n if n else v


def embed(texts: list[str]) -> np.ndarray:
    """list of strings -> float32 array (n, dim), L2-normalised."""
    global _model, USING_REAL_MODEL
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            USING_REAL_MODEL = True
        except Exception:
            _model = "toy"
            print("[embed.py] sentence-transformers unavailable -> using toy word-hash embeddings")
    if _model == "toy":
        return np.vstack([_toy_embed(t) for t in texts])
    return _model.encode(texts, normalize_embeddings=True).astype("float32")
