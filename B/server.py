from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.chatbot import answer_query
from src.ingest import main as ingest_main

app = FastAPI()

# Allow your React frontend to call FastAPI
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],         # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],         # allow all headers

)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str] | None = None
@app.get("/")
def root():
    return {"message": "Backend is running. Use /query for chatbot requests."}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    result = answer_query(req.question)
    return QueryResponse(answer=result["answer"], sources=result["sources"])

@app.post("/ingest")
def ingest():
    ingest_main()
    return {"status": "ok", "message": "Embeddings rebuilt"}
