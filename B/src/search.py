import pickle
import numpy as np
import faiss
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from .config import FAISS_INDEX_PATH, FAISS_STORE_PATH

# Load FAISS index and store
index = faiss.read_index(FAISS_INDEX_PATH)
with open(FAISS_STORE_PATH, "rb") as f:
    store = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")  # same as ingest

def search_documents(query: str, filters: List[str] = []) -> List[Dict]:
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

    # Optional: sort by similarity descending
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:10]
