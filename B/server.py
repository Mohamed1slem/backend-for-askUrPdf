from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.chatbot import answer_query
from src.ingest import main as ingest_main
from src.search import search_documents  # your FAISS search function

app = FastAPI()

# Allow your React frontend to call FastAPI
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Chatbot endpoint ---
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None

@app.get("/")
def root():
    return {"message": "Backend is running. Use /query for chatbot requests."}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    result = answer_query(req.question)
    return QueryResponse(answer=result["answer"], sources=result["sources"])

# --- Document search endpoint ---
class SearchRequest(BaseModel):
    query: str
    filters: Optional[List[str]] = []

class SearchResult(BaseModel):
    id: str
    title: str
    chunk: str
    similarity: float
    source: Optional[str] = None
    page: Optional[int] = 0
    metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]

@app.post("/search", response_model=SearchResponse)
def search_docs(req: SearchRequest):
    """
    Uses FAISS embeddings to find relevant document chunks
    based on the employee's query.
    Returns top chunks with similarity scores.
    """
    docs = search_documents(req.query, req.filters)
    
    # Convert to Pydantic response format
    results = []
    for doc in docs:
        results.append(
            SearchResult(
                id=doc.get("id", ""),
                title=doc.get("title", ""),
                chunk=doc.get("chunk", ""),
                similarity=float(doc.get("similarity", 0.0)),
                source=doc.get("source"),
                page=int(doc.get("page", 0)),
                metadata=doc.get("metadata", {}),
            )
        )
    return SearchResponse(results=results)

# --- Rebuild embeddings endpoint ---
@app.post("/ingest")
def ingest():
    """
    Reprocess cleaned documents, build embeddings, and save FAISS index.
    """
    ingest_main()
    return {"status": "ok", "message": "Embeddings rebuilt"}
