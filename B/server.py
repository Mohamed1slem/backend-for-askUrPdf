# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from src.chatbot import answer_query
from src.ingest import main as ingest_main
from src.search import search_documents  # FAISS search function

from src.retriever import Retriever

retriever = Retriever()  # global retriever instance
# -----------------------------
# Logging configuration
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="AI Assistant & Document Search API")

# Allow your React frontend to call FastAPI
origins = ["*"]  # Change to your frontend origin in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Models
# -----------------------------
# Chatbot
class QueryRequest(BaseModel):
    question: str

class SourceInfo(BaseModel):
    source: str
    similarity: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]

# Document search
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

# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    return {"message": "Backend is running. Use /query or /search endpoints."}

# ---- Chatbot ----
@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    logger.info(f"[QUERY] Received question: {req.question}")
    result = answer_query(req.question)

    answer = result.get("answer", "No answer generated.")
    sources = result.get("sources", [])
    logger.info(f"[QUERY] Answer: {answer}, Sources: {len(sources)}")

    return QueryResponse(answer=answer, sources=sources)

# ---- Document search ----
@app.post("/search", response_model=SearchResponse)
def search_docs(req: SearchRequest):
    logger.info(f"[SEARCH] Query: {req.query}, Filters: {req.filters}")

    docs = search_documents(req.query, req.filters) or []

    results = []
    for i, doc in enumerate(docs, 1):
        results.append(
            SearchResult(
                id=str(doc.get("id", f"doc-{i}")),
                title=doc.get("title", "Untitled"),
                chunk=doc.get("chunk", ""),
                similarity=float(doc.get("similarity", 0.0)),
                source=doc.get("source", "unknown"),
                page=int(doc.get("page", 0)),
                metadata=doc.get("metadata", {}),
            )
        )

    logger.info(f"[SEARCH] Returning {len(results)} results for query='{req.query}'")
    return SearchResponse(results=results)

# ---- Rebuild embeddings ----
@app.post("/ingest")
def ingest():
    logger.info("[INGEST] Rebuilding FAISS embeddings...")
    ingest_main()
    logger.info("[INGEST] Embeddings rebuilt successfully.")
    return {"status": "ok", "message": "Embeddings rebuilt"}

# -----------------------------
# Debug info for startup
# -----------------------------
@app.on_event("startup")
def startup_event():
    logger.info("FastAPI backend started and ready!")
