from typing import List, Dict

from .retriever import Retriever

def search_documents(query: str, filters: list[str] = []) -> List[Dict]:
    """
    Perform semantic search using the FAISS-backed retriever and
    return a simplified list of results compatible with the API schema:
    [{"id": str, "title": str, "similarity": float}]

    Notes:
    - "filters" are currently not applied; implement category mapping
      when metadata is available in the store.
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