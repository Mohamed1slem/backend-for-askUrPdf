# search.py
import os
import unicodedata
import logging
from typing import List, Dict, Optional
from .retriever import Retriever

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Helpers
# -----------------------------
def _normalize(value: str) -> str:
    if not isinstance(value, str):
        return ""
    v = unicodedata.normalize("NFD", value)
    v = "".join(c for c in v if unicodedata.category(c) != "Mn")
    v = v.lower().replace(" ", "-")
    return v

def _category_from_source(source_path: str) -> str:
    if not source_path:
        return "unknown"
    norm = os.path.normpath(source_path)
    top = norm.split(os.sep)[0]
    return top

def _filters_match(category: str, filters: List[str], metadata: Optional[Dict] = None) -> bool:
    filters = [f for f in (filters or []) if isinstance(f, str) and f.strip()]
    if not filters:
        return True

    cat_norm = _normalize(category)
    accepted = set(_normalize(f) for f in filters)

    # Aliases for categories
    aliases = {
        "conventions": {"convention"},
        "depot-vente": {"depot", "depotvente", "depot_vente", "dépôt-vente", "dépôt", "depot vente"},
        "guide-ngbss": {"guide", "ngbss", "guide-ngbss"},
        "offres": {"offre", "offers"},
        "offres-en-arabe": {"offre-ar", "offers-ar", "arabe"},
    }

    cat_token_map = {
        "convention": "conventions",
        "dépot-vente": "depot-vente",
        "depot-vente": "depot-vente",
        "guide-ngbss": "guide-ngbss",
        "offres": "offres",
        "offres-en-arabe": "offres-en-arabe",
    }

    canonical = cat_token_map.get(cat_norm, cat_norm)
    if canonical in accepted:
        return True
    for canon, alias_set in aliases.items():
        if canonical == canon and (canon in accepted or any(a in accepted for a in alias_set)):
            return True

    if metadata:
        for key in ("category", "partner", "offer_type", "sector"):
            val = _normalize(str(metadata.get(key, "")))
            if val in accepted:
                return True

    return cat_norm in accepted

# -----------------------------
# Main search function
# -----------------------------
def search_documents(query: str, filters: Optional[List[str]] = None) -> List[Dict]:
    if not query:
        logger.warning("[SEARCH] Empty query received")
        return []

    filters = filters or []
    filters = [f.strip() for f in filters if f.strip()]
    logger.info(f"[SEARCH] Query='{query}', Filters={filters}")

    retriever = Retriever()
    chunks = retriever.search(query, top_k=20)
    logger.info(f"[SEARCH] Retrieved {len(chunks)} chunks from retriever")

    results: List[Dict] = []
    for i, c in enumerate(chunks, 1):
        orig = c.get("original_source") or c.get("source") or ""
        category = _category_from_source(orig)

        if filters and not _filters_match(category, filters, c.get("metadata")):
            logger.debug(f"[SEARCH] Skipping chunk {i} due to filter mismatch: category='{category}'")
            continue

        title = c.get("source") or os.path.basename(orig) or f"Result {i}"
        sim = float(c.get("boosted_similarity", c.get("similarity", 0.0)))
        text = c.get("text") or ""

        logger.debug(f"[SEARCH] Chunk {i}: title='{title}', similarity={sim}, source='{orig}'")

        results.append({
            "id": str(i),
            "title": title,
            "chunk": text,
            "similarity": sim,
            "confidence": c.get("confidence"),
            "source": os.path.basename(orig) if orig else title,
            "page": c.get("page", 0),
            "metadata": c.get("metadata", {}),
        })

    logger.info(f"[SEARCH] Returning {len(results[:10])} results")
    return results[:10]
