import pickle
import numpy as np
import faiss
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from .config import FAISS_INDEX_PATH, FAISS_STORE_PATH
from .retriever import Retriever

# ---------------- FAISS-based function ----------------
# Load FAISS index and store
index = faiss.read_index(FAISS_INDEX_PATH)
with open(FAISS_STORE_PATH, "rb") as f:
    store = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")  # same as ingest

def predict(query: str, filters: List[str] = []) -> List[Dict]:
    """
    FAISS-based semantic search returning detailed results
    including chunk text and category.
    """
    if not query:
        return []

    # Embed query
    q_vec = model.encode([query], normalize_embeddings=True)
    q_vec = np.array(q_vec, dtype="float32")

    # Search in FAISS
    k = 20  # get more results to allow filtering
    D, I = index.search(q_vec, k)

    results = []
    for score, idx in zip(D[0], I[0]):
        if idx == -1:
            continue

        doc_id = store["ids"][idx]
        text = store["texts"][idx]
        source = store["sources"][idx]

        category = source.split("/")[0]
        if filters and category not in filters:
            continue

        results.append({
            "id": doc_id,
            "title": source.split("/")[-1],
            "chunk": text,
            "similarity": float(score),
            "category": category,
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:10]

# ---------------- Retriever-based function ----------------
def search(query: str, filters: list[str] = []) -> List[Dict]:
    """
    Retriever-based semantic search returning simplified results
    compatible with API schema: [{"id": str, "title": str, "similarity": float}]
    """
    retriever = Retriever()
    chunks = retriever.search(query)

    results: List[Dict] = []
    for i, c in enumerate(chunks, start=1):
        title = c.get("source") or c.get("original_source") or f"Result {i}"
        sim = float(c.get("boosted_similarity", c.get("similarity", 0.0)))
        results.append({
            "id": str(i),
            "title": title,
            "similarity": sim,
        })

    return results
