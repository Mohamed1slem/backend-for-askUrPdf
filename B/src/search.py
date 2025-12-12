# Example search logic — replace with FAISS, Chroma, or your embedding DB

import json

def search_documents(query: str, filters: list[str] = []):
    """
    Return documents + similarity score.
    Connect this to your embeddings using FAISS or your RAG pipeline.
    """

    # Placeholder — replace with your real vector search
    docs = [
        {
            "id": "1",
            "title": "Convention 2024",
            "similarity": 92.7
        },
        {
            "id": "2",
            "title": "Offre Entreprise Premium",
            "similarity": 84.3
        }
    ]

    return docs