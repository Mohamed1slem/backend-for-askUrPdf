import os
import pickle
from typing import List, Dict, Any, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from .config import (
    DATA_DIR, EMBEDDINGS_DIR, FAISS_INDEX_PATH, FAISS_STORE_PATH,
    EMBEDDING_MODEL_NAME, USE_OPENAI_EMBEDDINGS, OPENAI_EMBEDDING_MODEL, BASE_DIR
)
from .pipeline import load_all_files, build_chunks_for_file, build_chunks_with_links

def build_corpus() -> List[Dict[str, Any]]:
    """Scan DATA_DIR/raw and DATA_DIR/cleaned for files, extract text, clean and chunk.

    Phase-3: also inject linking metadata (source_links, related_links) produced by
    pipeline.build_chunks_with_links, without altering chunking or embeddings logic.
    """
    corpus: List[Dict[str, Any]] = []
    roots = [
        os.path.join(DATA_DIR, "raw"),
        os.path.join(DATA_DIR, "cleaned"),
    ]

    # Build a document-level map of links using the pipeline's Phase-3 output
    doc_links: Dict[str, Dict[str, List[str]]] = {}
    for root in roots:
        if not os.path.isdir(root):
            continue
        try:
            lchunks = build_chunks_with_links(root)
            for lc in lchunks:
                # Use the first source link as the document key
                src_links = lc.get("source_links", []) or []
                if not src_links:
                    continue
                key = os.path.normpath(src_links[0])
                # Store once per document
                if key not in doc_links:
                    doc_links[key] = {
                        "source_links": src_links,
                        "related_links": list(lc.get("related_links", []) or []),
                    }
        except Exception:
            # Linking is best-effort; proceed even if linking assembly fails
            pass

    seen_hashes = set()
    for root in roots:
        if not os.path.isdir(root):
            continue
        for path in load_all_files(root):
            try:
                chunks = build_chunks_for_file(path)
                for c in chunks:
                    # Dedup by chunk hash (preserve existing ingestion behavior)
                    h = c.get("hash")
                    if not h:
                        # Fallback: hash text content deterministically
                        try:
                            import hashlib
                            h = hashlib.sha256((c.get("text") or "").encode("utf-8", errors="ignore")).hexdigest()
                            c["hash"] = h
                        except Exception:
                            h = None
                    if h and h in seen_hashes:
                        continue
                    if h:
                        seen_hashes.add(h)

                    # Inject Phase-3 linking metadata
                    original = c.get("original_source") or c.get("source") or ""
                    if original:
                        # Normalize to project-relative path for lookup
                        if os.path.isabs(original):
                            try:
                                key = os.path.relpath(original, BASE_DIR)
                            except Exception:
                                key = original
                        else:
                            key = os.path.normpath(original)
                    else:
                        key = ""

                    links_info = doc_links.get(key)
                    if links_info:
                        c["source_links"] = list(links_info.get("source_links", []))
                        c["related_links"] = list(links_info.get("related_links", []))
                    else:
                        # Fallback: at least include this chunk's own source path
                        c["source_links"] = [key] if key else []
                        c["related_links"] = []

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
        # Phase-3 linking metadata
        "source_links": [c.get("source_links", []) for c in corpus],
        "related_links": [c.get("related_links", []) for c in corpus],
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
