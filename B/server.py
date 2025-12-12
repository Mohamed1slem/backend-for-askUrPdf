import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from src.search import predict, search      # <-- your search functions
from src.chatbot import answer_query        # <-- your answer_query function

app = FastAPI()

# --------------------
# CORS configuration
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Request Models
# --------------------
class SearchRequest(BaseModel):
    query: str
    filters: Optional[List[str]] = []

class QueryRequest(BaseModel):
    question: str

# --------------------
# Response Models
# --------------------
class SearchResult(BaseModel):
    id: str
    title: str
    chunk: Optional[str] = ""
    similarity: float
    category: Optional[str] = "unknown"

class SearchResponse(BaseModel):
    results: List[SearchResult]

# --------------------
# /query endpoint
# --------------------
@app.post("/query")
def query_endpoint(req: QueryRequest):
    """
    Accepts JSON: { "question": "..." }
    Returns answer from answer_query()
    """
    question_text = req.question
    answer_data = answer_query(question_text)
    return answer_data

# --------------------
# /predict endpoint
# --------------------
@app.post("/predict", response_model=List[SearchResult])
def predict_docs(req: SearchRequest):
    docs = predict(req.query, req.filters)
    return [
        SearchResult(
            id=doc.get("id", "unknown_id"),
            title=doc.get("title", "Untitled"),
            chunk=doc.get("chunk", ""),
            similarity=doc.get("similarity", 0.0),
            category=doc.get("category", "unknown")
        )
        for doc in docs
    ]

# --------------------
# /search endpoint
# --------------------
@app.post("/search", response_model=SearchResponse)
def search_docs(req: SearchRequest):
    docs = search(req.query, req.filters)
    
    results = []
    for doc in docs:
        # Prefer folder-based category if source exists, otherwise use doc['category']
        if "source" in doc and doc["source"]:
            folder_name = os.path.basename(os.path.dirname(doc["source"])) or "unknown"
            category = folder_name
        else:
            category = doc.get("category", "unknown")

        results.append(
            SearchResult(
                id=doc.get("id", "unknown_id"),
                title=doc.get("title", "Untitled"),
                similarity=doc.get("similarity", 0.0),
                chunk=doc.get("chunk", ""),
                category=category
            )
        )

    return SearchResponse(results=results)
