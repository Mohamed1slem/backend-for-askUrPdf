import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from .config import FAISS_INDEX_PATH, FAISS_STORE_PATH, EMBEDDING_MODEL_NAME, TOP_K

class Retriever:
    def __init__(self):
        # Load FAISS index
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}")
        self.index = faiss.read_index(FAISS_INDEX_PATH)

        # Load metadata store (Pickle)
        if not os.path.exists(FAISS_STORE_PATH):
            raise FileNotFoundError(f"Metadata not found at {FAISS_STORE_PATH}")
        with open(FAISS_STORE_PATH, "rb") as fh:
            self.store = pickle.load(fh)

        # Load embedding model
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def search(self, query: str, top_k: int = TOP_K, min_similarity: float = 60.0, username: str = None) -> List[Dict[str, Any]]:
        results = []
        
        if username:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            user_vector_db_dir = os.path.join(base_dir, "data", "user_vector_db", username)
            index_path = os.path.join(user_vector_db_dir, "index_local.bin")
            store_path = os.path.join(user_vector_db_dir, "faiss_store.pkl")
            
            if os.path.exists(index_path) and os.path.exists(store_path):
                try:
                    u_index = faiss.read_index(index_path)
                    with open(store_path, "rb") as fh:
                        u_store = pickle.load(fh)
                    results = self._search_index(query, u_index, u_store, top_k)
                except Exception as e:
                    print(f"Error loading user index: {e}")
                    
        return sorted(results, key=lambda x: x["boosted_similarity"], reverse=True)[:top_k]

    def _search_index(self, query: str, index, store, top_k: int) -> List[Dict[str, Any]]:
        q_vec = self.model.encode([query], normalize_embeddings=True)
        q_vec = np.array(q_vec, dtype="float32")
        scores, idxs = index.search(q_vec, top_k)

        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1:
                continue

            chunk = {
                "id": store["ids"][idx],
                "text": store["texts"][idx],
                "source": store["sources"][idx],
                "original_source": store["original_sources"][idx],
                "page": store["pages"][idx],
                "metadata": store["metadata"][idx],
                "hash": store["hashes"][idx],
                "links": store["links"][idx],
            }

            percentage = round(score * 100, 2)
            chunk["score"] = float(score)
            chunk["similarity"] = percentage
            chunk["boosted_similarity"] = percentage

            results.append(chunk)

            for linked_id in chunk["links"]:
                try:
                    linked_idx = store["ids"].index(linked_id)
                    linked_chunk = {
                        "id": store["ids"][linked_idx],
                        "text": store["texts"][linked_idx],
                        "source": store["sources"][linked_idx],
                        "original_source": store["original_sources"][linked_idx],
                        "page": store["pages"][linked_idx],
                        "metadata": store["metadata"][linked_idx],
                        "hash": store["hashes"][linked_idx],
                        "links": store["links"][linked_idx],
                        "score": float(score),
                        "similarity": percentage,
                        "boosted_similarity": percentage - 5,
                    }
                    results.append(linked_chunk)
                except ValueError:
                    continue

        return results

def expand_with_related(base_results, store, max_extra=4):
    """
    Expand search results with related chunks using the 'links' field.
    base_results: list of chunks returned by retriever.search
    store: FAISS metadata store (dict with ids, texts, etc.)
    max_extra: maximum number of related chunks to add
    """
    expanded_texts = []
    seen_ids = set()

    for chunk in base_results:
        expanded_texts.append(chunk["text"])
        seen_ids.add(chunk.get("id"))

        for linked_id in chunk.get("links", []):
            if linked_id in seen_ids:
                continue
            try:
                linked_idx = store["ids"].index(linked_id)
                expanded_texts.append(store["texts"][linked_idx])
                seen_ids.add(linked_id)
                if len(expanded_texts) >= len(base_results) + max_extra:
                    break
            except ValueError:
                continue

    return expanded_texts