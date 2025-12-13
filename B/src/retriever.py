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
            hsh = self.store.get("hashes", [""])[idx]

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
                    "hash": hsh,
                    "score": float(score),
                    "similarity": percentage,
                    "boosted_similarity": boosted_percentage,
                    "boost": boost
                })

        # Sort by boosted similarity and keep top_k chunks directly
        top_chunks = sorted(results, key=lambda x: x["boosted_similarity"], reverse=True)[:top_k]

        return top_chunks


def expand_with_related(base_results: List[Dict[str, Any]], store: Dict[str, Any], max_extra: int = 4) -> List[str]:
    """
    Expand first-stage retrieval results with Phase-3 related documents.

    Rules:
    - Keep original retrieved chunks (preserve order)
    - Add up to `max_extra` extra chunks whose metadata.source_links intersect with any
      link in the union of base_results' metadata.related_links
    - Avoid duplicates (by hash/text)
    - Deterministic ordering: extras follow store index order

    Inputs:
    - base_results: List of dicts with keys at least {"text", "metadata", "hash"}
      where metadata may include "source_links" and "related_links". If these are
      missing in metadata, this function falls back to values in `store` by matching hash.
    - store: the persisted FAISS store dictionary as saved by ingestion, expected keys:
      "texts", "hashes", and optionally "source_links", "related_links" (lists aligned by index).

    Returns:
    - List[str] containing the base texts followed by up to `max_extra` expanded texts.
    """
    # Collect base texts and hashes (to avoid duplicates later)
    base_texts: List[str] = []
    base_hashes: set = set()
    for r in base_results:
        txt = r.get("text", "")
        base_texts.append(txt)
        h = r.get("hash")
        if h:
            base_hashes.add(h)

    # Build a lookup from hash -> store index for fallback to store metadata
    hash_to_idx: Dict[str, int] = {}
    hashes = store.get("hashes", [])
    for i, h in enumerate(hashes):
        if h and h not in hash_to_idx:
            hash_to_idx[h] = i

    # Union of related links from base results
    related_links_set = set()
    for r in base_results:
        md = r.get("metadata", {}) or {}
        rl = md.get("related_links")
        if rl is None:
            # Fallback via store if available
            h = r.get("hash")
            if h and h in hash_to_idx:
                idx = hash_to_idx[h]
                rl = store.get("related_links", [None] * len(hashes))[idx]
        if rl:
            for p in rl:
                if p:
                    related_links_set.add(os.path.normpath(p))

    if not related_links_set or max_extra <= 0:
        return base_texts

    # Scan store for candidates whose source_links intersect with related_links_set
    source_links_all = store.get("source_links", [])
    texts_all = store.get("texts", [])
    hashes_all = hashes

    candidates: List[int] = []
    for i in range(min(len(texts_all), len(source_links_all))):
        sl = source_links_all[i] if i < len(source_links_all) else []
        if not sl:
            continue
        # Normalize and test intersection
        for p in sl:
            if os.path.normpath(p) in related_links_set:
                candidates.append(i)
                break

    # Deterministic: keep store index order; filter out duplicates
    extra_texts: List[str] = []
    seen_texts = set(base_texts)
    for i in candidates:
        if len(extra_texts) >= max_extra:
            break
        h = hashes_all[i] if i < len(hashes_all) else None
        if h and h in base_hashes:
            continue
        t = texts_all[i]
        if t in seen_texts:
            continue
        extra_texts.append(t)
        seen_texts.add(t)

    return base_texts + extra_texts
