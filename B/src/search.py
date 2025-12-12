import pickle
import numpy as np
import faiss
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
from .config import FAISS_INDEX_PATH, FAISS_STORE_PATH
from .retriever import Retriever

# ---------------- FAISS-based setup ----------------
index = faiss.read_index(FAISS_INDEX_PATH)
with open(FAISS_STORE_PATH, "rb") as f:
    store = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")  # same as ingest

# ---------------- Helper: extract relevant snippet ----------------
def extract_relevant_snippet(chunk: str, query: str, model) -> str:
    """
    Splits the chunk into sentences and returns the sentence
    most semantically similar to the query.
    """
    sentences = [s.strip() for s in chunk.split(". ") if s.strip()]
    if not sentences:
        return chunk[:200]  # fallback snippet

    query_vec = model.encode([query], convert_to_tensor=True)
    sentence_vecs = model.encode(sentences, convert_to_tensor=True)

    # Compute cosine similarities
    cos_scores = util.cos_sim(query_vec, sentence_vecs)[0]

    # Get the most similar sentence
    best_idx = int(np.argmax(cos_scores))
    return sentences[best_idx]

# ---------------- FAISS-based function ----------------
def predict(query: str, filters: List[str] = []) -> List[Dict]:
    if not query:
        return []

    q_vec = model.encode([query], normalize_embeddings=True)
    q_vec = np.array(q_vec, dtype="float32")

    k = 20
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

        snippet = extract_relevant_snippet(text, query, model)

        results.append({
            "id": doc_id,
            "title": source.split("/")[-1],
            "chunk": snippet,
            "similarity": float(score),
            "category": category,
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:10]

# ---------------- Retriever-based function ----------------
def search(query: str, filters: List[str] = []) -> List[Dict]:
    retriever = Retriever()
    chunks = retriever.search(query)

    results: List[Dict] = []
    for i, c in enumerate(chunks, start=1):
        title = c.get("source") or c.get("original_source") or f"Result {i}"
        sim = float(c.get("boosted_similarity", c.get("similarity", 0.0)))

        # Optional: also extract snippet if chunk exists
        text = c.get("text") or ""
        snippet = extract_relevant_snippet(text, query, model) if text else ""

        results.append({
            "id": str(i),
            "title": title,
            "chunk": snippet,
            "similarity": sim,
            "category": "unknown",
        })

    return results
