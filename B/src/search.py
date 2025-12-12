import os
import unicodedata
from typing import List, Dict

from .retriever import Retriever


def _normalize(value: str) -> str:
    if not isinstance(value, str):
        return ""
    # remove accents, lowercase, collapse spaces and separators
    v = unicodedata.normalize("NFD", value)
    v = "".join(c for c in v if unicodedata.category(c) != "Mn")
    v = v.lower().replace(" ", "-")
    return v


def _category_from_source(source_path: str) -> str:
    # source_path is relative path like "Guide NGBSS/xxx_chunk1.txt"
    if not source_path:
        return ""
    norm = os.path.normpath(source_path)
    top = norm.split(os.sep)[0]
    return top


def _filters_match(category: str, filters: List[str], metadata: Dict | None = None) -> bool:
    if not filters:
        return True
    cat_norm = _normalize(category)
    # Accept both simplified tokens and literal folder names
    accepted = set(_normalize(f) for f in filters)
    # Common aliases mapping
    aliases = {
        "conventions": {"convention"},
        "depot-vente": {"depot", "depotvente", "depot_vente", "dépôt-vente", "dépôt", "depot vente"},
        "guide-ngbss": {"guide", "ngbss", "guide-ngbss"},
        "offres": {"offre", "offers"},
        "offres-en-arabe": {"offre-ar", "offers-ar", "arabe"},
    }
    # Map category folder to canonical token
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
    # check aliases
    for canon, alias_set in aliases.items():
        if canonical == canon and (canon in accepted or any(a in accepted for a in alias_set)):
            return True
    # also allow direct match with raw normalized folder name
    # Also match against metadata values (category, partner, offer_type, sector)
    if metadata:
        for key in ("category", "partner", "offer_type", "sector"):
            val = _normalize(str(metadata.get(key, "")))
            if val and (val in accepted):
                return True
    return cat_norm in accepted


def search_documents(query: str, filters: List[str] = []) -> List[Dict]:
    """
    Perform semantic search using the FAISS-backed retriever and return a
    simplified list compatible with the API schema:
      [{"id": str, "title": str, "similarity": float}]

    Filters are optional and can accept tokens like:
      ["conventions", "depot-vente", "guide-ngbss", "offres", "offres-en-arabe"]
    or literal folder names. Additional structured filters are not yet applied.
    """
    if not query:
        return []

    retriever = Retriever()
    chunks = retriever.search(query, top_k=20)

    results: List[Dict] = []
    i = 0
    for c in chunks:
        orig = c.get("original_source") or c.get("source") or ""
        category = _category_from_source(orig)
        if filters and not _filters_match(category, filters, c.get("metadata")):
            continue
        i += 1
        title = c.get("source") or os.path.basename(orig) or f"Result {i}"
        sim = float(c.get("boosted_similarity", c.get("similarity", 0.0)))

        # Optional: also extract snippet if chunk exists
        text = c.get("text") or ""
        snippet = ""

        results.append({
            "id": str(i),
            "title": title,
            "chunk": c.get("text", ""),
            "similarity": sim,
            "source": os.path.basename(orig) if orig else title,
            "page": c.get("page", 0),
            "metadata": c.get("metadata", {}),
        })

    # cap to top 10 for API response stability
    return results[:10]


def search_advanced(query: str, filters: List[str] = []) -> List[Dict]:
    """
    Advanced results including chunk text and derived category. Useful for
    internal tooling or evaluation pipelines.
    """
    if not query:
        return []
    retriever = Retriever()
    chunks = retriever.search(query, top_k=20)

    out: List[Dict] = []
    for c in chunks:
        orig = c.get("original_source") or c.get("source") or ""
        category = _category_from_source(orig)
        if filters and not _filters_match(category, filters):
            continue
        out.append({
            "id": c.get("id", ""),
            "title": c.get("source") or os.path.basename(orig),
            "chunk": c.get("text", ""),
            "similarity": float(c.get("boosted_similarity", c.get("similarity", 0.0))),
            "category": category,
            "source": c.get("source"),
            "original_source": orig,
            "page": c.get("page", 0),
            "metadata": c.get("metadata", {}),
        })
    return out[:10]


def predict(query: str, filters: List[str] = []) -> List[Dict]:
    """
    Backwards-compatible detailed search function.

    Returns a richer structure per item, including:
      {"id", "title", "chunk", "similarity", "category"}

    Uses the same FAISS-backed Retriever as search_documents and applies
    the same folder-derived category filtering.
    """
    if not query:
        return []

    retriever = Retriever()
    chunks = retriever.search(query, top_k=20)

    results: List[Dict] = []
    for c in chunks:
        orig = c.get("original_source") or c.get("source") or ""
        category = _category_from_source(orig)
        if filters and not _filters_match(category, filters):
            continue
        results.append({
            "id": c.get("id", ""),
            "title": c.get("source") or os.path.basename(orig),
            "chunk": c.get("text", ""),
            "similarity": float(c.get("boosted_similarity", c.get("similarity", 0.0))),
            "category": category,
        })

    # Keep top 10 similar items
    results.sort(key=lambda x: x.get("similarity", 0.0), reverse=True)
    return results[:10]
