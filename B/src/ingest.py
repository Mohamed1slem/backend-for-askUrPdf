import os
import pickle
from typing import List, Dict, Any

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from .config import (
    CLEANED_DIR, EMBEDDINGS_DIR, FAISS_INDEX_PATH, FAISS_STORE_PATH,
    EMBEDDING_MODEL_NAME, CHUNK_SIZE, CHUNK_OVERLAP
)
from .utils import load_text_files, chunk_text, rel_path_from_base

def build_corpus() -> List[Dict[str, Any]]:
    """
    Load cleaned docs, chunk them, and return a corpus list of dicts:
    {
      'id': str,
      'text': str,
      'source': str,     # relative file path
    }
    """
    corpus = []
    files = load_text_files(CLEANED_DIR)
    uid = 0
    for path, content in files:
        source = rel_path_from_base(CLEANED_DIR, path)
        chunks = chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP)
        for ch in chunks:
            corpus.append({
                "id": f"doc_{uid}",
                "text": ch,
                "source": source,
            })
            uid += 1
    return corpus

def embed_corpus(corpus: List[Dict[str, Any]]) -> np.ndarray:
    """
    Create embeddings for all corpus texts.
    """
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    texts = [c["text"] for c in corpus]
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
    }
    with open(FAISS_STORE_PATH, "wb") as fh:
        pickle.dump(store, fh)

def main():
    print(f"Loading cleaned docs from: {CLEANED_DIR}")
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
