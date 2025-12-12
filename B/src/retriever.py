import os
import pickle
from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .config import FAISS_INDEX_PATH, FAISS_STORE_PATH, EMBEDDING_MODEL_NAME, TOP_K

class Retriever:
    def __init__(self):
        # Load FAISS index
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        # Load metadata store
        with open(FAISS_STORE_PATH, "rb") as fh:
            self.store = pickle.load(fh)
        # Load embedding model
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def _keyword_boost(self, query: str, text: str) -> int:
        """Keyword overlap boost with special weights for telecom terms."""
        q_words = set(query.lower().split())
        t_words = set(text.lower().split())
        boost = 0
        # General overlap
        overlap = len(q_words & t_words)
        boost += overlap * 2
        # Special domain boosts
        special_weights = {
            "fibre": 5,
            "mbps": 5,
            "tarif": 4,
            "idoom": 3,
            "adsl": 3,
            "vdsl": 3,
            "convention": 2,
            "établissement": 2
        }
        for w in q_words:
            if w in special_weights and w in t_words:
                boost += special_weights[w]
        return boost

    def search(self, query: str, top_k: int = TOP_K, min_similarity: float = 60.0) -> List[Dict[str, Any]]:
        # Encode query
        q_vec = self.model.encode([query], normalize_embeddings=True)
        q_vec = np.array(q_vec, dtype="float32")
        scores, idxs = self.index.search(q_vec, top_k)

        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1:
                continue
            src = self.store["sources"][idx]
            txt = self.store["texts"][idx]
            orig = self.store.get("original_sources", [""])[idx]
            page = self.store.get("pages", [0])[idx]
            meta = self.store.get("metadata", [{}])[idx]

            src_name = os.path.basename(src)

            # Convert FAISS score to similarity percentage
            similarity = 1 / (1 + score)
            percentage = round(similarity * 100, 2)

            # Apply keyword boost
            boost = self._keyword_boost(query, txt)
            boosted_percentage = min(100.0, percentage + boost)

            if boosted_percentage >= min_similarity:
                results.append({
                    "text": txt,
                    "source": src_name,
                    "original_source": orig or src,
                    "page": page,
                    "metadata": meta,
                    "score": float(score),
                    "similarity": percentage,
                    "boosted_similarity": boosted_percentage,
                    "boost": boost
                })

        # Sort by boosted similarity and keep top_k chunks directly
        top_chunks = sorted(results, key=lambda x: x["boosted_similarity"], reverse=True)[:top_k]

        return top_chunks
