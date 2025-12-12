import os
import pickle
from typing import List, Dict, Any

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
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in load_all_files(root):
            try:
                corpus.extend(build_chunks_for_file(path))
            except Exception:
                continue
    return corpus

def embed_corpus(corpus: List[Dict[str, Any]]) -> np.ndarray:
    """Create embeddings for all corpus texts using ST model or OpenAI if enabled."""
    texts = [c["text"] for c in corpus]
    if USE_OPENAI_EMBEDDINGS and os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI()
            vectors = []
            batch = 128
            for i in range(0, len(texts), batch):
                chunk = texts[i:i+batch]
                resp = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=chunk)
                vectors.extend([d.embedding for d in resp.data])
            return np.array(vectors, dtype="float32")
        except Exception:
            pass
    # Fallback to SentenceTransformers
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    vectors = model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
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
