import os
import pickle
from typing import List, Dict, Any, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from .config import (
    DATA_DIR, EMBEDDINGS_DIR, FAISS_INDEX_PATH, FAISS_STORE_PATH,
    EMBEDDING_MODEL_NAME, USE_OPENAI_EMBEDDINGS, OPENAI_EMBEDDING_MODEL
)
from .pipeline import load_all_files, build_chunks_for_file

def build_corpus() -> List[Dict[str, Any]]:
    """Scan DATA_DIR/raw and DATA_DIR/cleaned for files, extract text, clean and chunk."""
    corpus: List[Dict[str, Any]] = []
    roots = [
        os.path.join(DATA_DIR, "raw"),
        os.path.join(DATA_DIR, "cleaned"),
    ]
    seen_hashes = set()
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in load_all_files(root):
            try:
                chunks = build_chunks_for_file(path)
                for c in chunks:
                    h = c.get("hash")
                    if h and h in seen_hashes:
                        continue
                    if h:
                        seen_hashes.add(h)
                    corpus.append(c)
            except Exception:
                continue
    return corpus

def _embed_batch_openai(client, model: str, texts: List[str]) -> List[List[float]]:
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]


def embed_corpus(corpus: List[Dict[str, Any]]) -> np.ndarray:
    """Create embeddings for all corpus texts using ST model or OpenAI if enabled."""
    texts = [c["text"] for c in corpus]
    if USE_OPENAI_EMBEDDINGS and os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI()
            vectors: List[List[float]] = []
            batch = 64
            for i in range(0, len(texts), batch):
                chunk = texts[i:i+batch]
                vectors.extend(_embed_batch_openai(client, OPENAI_EMBEDDING_MODEL, chunk))
            return np.array(vectors, dtype="float32")
        except Exception:
            pass
    # Fallback to SentenceTransformers
    # Cache embeddings by chunk hash to avoid recomputation
    cache_path = os.path.join(EMBEDDINGS_DIR, "embedding_cache.pkl")
    cache: Dict[str, List[float]] = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as fh:
                cache = pickle.load(fh)
        except Exception:
            cache = {}

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    vectors_list: List[List[float]] = []
    to_update: Dict[str, List[float]] = {}
    for c in corpus:
        h = c.get("hash") or ""
        if h and h in cache:
            vectors_list.append(cache[h])
        else:
            v = model.encode([c["text"]], normalize_embeddings=True)
            vec = list(map(float, v[0]))
            vectors_list.append(vec)
            if h:
                to_update[h] = vec

    if to_update:
        cache.update(to_update)
        try:
            with open(cache_path, "wb") as fh:
                pickle.dump(cache, fh)
        except Exception:
            pass

    vectors = np.array(vectors_list, dtype="float32")
    return np.array(vectors, dtype="float32")

def save_faiss_index(vectors: np.ndarray, corpus: List[Dict[str, Any]]):
    """
    Save FAISS index and store mapping (id->metadata).
    """
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine if normalized embeddings
    index.add(vectors)

    faiss.write_index(index, FAISS_INDEX_PATH)

    store = {
        "ids": [c["id"] for c in corpus],
        "texts": [c["text"] for c in corpus],
        "sources": [c["source"] for c in corpus],
        "original_sources": [c.get("original_source", "") for c in corpus],
        "pages": [c.get("page", 0) for c in corpus],
        "metadata": [c.get("metadata", {}) for c in corpus],
        "hashes": [c.get("hash", "") for c in corpus],
    }
    with open(FAISS_STORE_PATH, "wb") as fh:
        pickle.dump(store, fh)

def main():
    print("Scanning and building corpus from data/raw and data/cleaned...")
    corpus = build_corpus()
    print(f"Total chunks: {len(corpus)}")

    print("Embedding corpus...")
    vectors = embed_corpus(corpus)

    print("Saving FAISS index and store...")
    save_faiss_index(vectors, corpus)

    print(f"Done. Index saved to {FAISS_INDEX_PATH} and store to {FAISS_STORE_PATH}")

if __name__ == "__main__":
    # Allow running standalone: python -m src.ingest
    main()
