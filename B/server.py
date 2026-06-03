# server.py
import sys
import os

# Prevent conflicts where Python resolves PyMuPDF's internal 'frontend' module
# to the React 'frontend' directory in the root of the project.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path = [p for p in sys.path if p and os.path.abspath(p) != parent_dir]
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
import uuid
from datetime import datetime

from src.chatbot import answer_query
from src.pipeline import run_pipeline
from src.ingest import run_ingest
from src.search import search_documents
import shutil
from src.retriever import Retriever
from src.auth import verify_password, get_password_hash, create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

from pymongo import MongoClient
from bson.objectid import ObjectId

# ---------------------------
# MongoDB Connection
# ---------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Default to local MongoDB if not set
try:
    client = MongoClient(MONGO_URI)
    db = client["chatbot_app"]
    users_collection = db["users"]
    chats_collection = db["chats"]
    chat_sessions_collection = db["chat_sessions"]
    comments_collection = db["comments"]
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# FastAPI App
# ---------------------------
app = FastAPI(title="AI Assistant & Document Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://askurpdf.vercel.app",
        "https://backend-for-askurpdf-production.up.railway.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Add OPTIONS handler for preflight requests
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    return {"status": "ok"}

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        # Fallback to Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


# ---------------------------
# Pydantic Models
# ---------------------------
class CommentRequest(BaseModel):
    text: str

class QueryRequest(BaseModel):
    question: str
    chat_id: str

class SourceInfo(BaseModel):
    source: str
    similarity: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]

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


class RegisterRequest(BaseModel):
    user: str
    pwd: str
    email: str

class LoginRequest(BaseModel):
    user: str
    pwd: str

class TokenResponse(BaseModel):
    accessToken: str
    user: str
    email: Optional[str] = None

# ---------------------------
# Routes
# ---------------------------
@app.get("/")
def root():
    return {"message": "Backend is running."}

# ---- Auth (Login / Register) ----
@app.post("/register")
def register_user(req: RegisterRequest):
    try:
        if users_collection.find_one({"username": req.user}):
            raise HTTPException(status_code=400, detail="Username already registered")
        if users_collection.find_one({"email": req.email}):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_pwd = get_password_hash(req.pwd)
        users_collection.insert_one({
            "username": req.user,
            "email": req.email,
            "hashed_password": hashed_pwd,
            "role": "user"
        })
        return {"message": "User registered successfully"}
    except Exception as e:
        print(f"ERROR inside /register: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth", response_model=TokenResponse)
def login_for_access_token(req: LoginRequest, response: Response):
    try:
        # Retrieve user from DB
        user_in_db = users_collection.find_one({"$or": [{"username": req.user}, {"email": req.user}]})
        
        if not user_in_db:
            raise HTTPException(status_code=401, detail="User not found")
        if not verify_password(req.pwd, user_in_db["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect password")
        
        # Generate JWT Token
        access_token = create_access_token(data={"sub": user_in_db["username"]})
        refresh_token = create_refresh_token(data={"sub": user_in_db["username"]})
        
        # Set HttpOnly cookies
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, samesite="lax")
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, samesite="lax")

        return {
            "accessToken": access_token, 
            "user": str(user_in_db["username"]),
            "email": str(user_in_db.get("email", ""))
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"ERROR inside /auth: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh")
def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        new_access_token = create_access_token(data={"sub": username})
        response.set_cookie(key="access_token", value=new_access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, samesite="lax")
        
        return {"accessToken": new_access_token, "user": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

# ---- Chatbot ----
@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest, current_user: str = Depends(get_current_user)):
    logger.info(f"[QUERY] User '{current_user}' asked: {req.question} in chat {req.chat_id}")
    
    # Resolve the filename associated with this chat session
    session = chat_sessions_collection.find_one({"chat_id": req.chat_id, "username": current_user})
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    
    filename = session.get("filename")
    result = answer_query(req.question, username=current_user, filename=filename)
    
    answer_text = result.get("answer", "No answer generated.")
    sources_list = result.get("sources") or []
    
    # Save chat to database
    chat_doc = {
        "chat_id": req.chat_id,
        "username": current_user,
        "question": req.question,
        "answer": answer_text,
        "sources": sources_list,
        "timestamp": datetime.utcnow()
    }
    try:
        chats_collection.insert_one(chat_doc)
    except Exception as e:
        logger.error(f"Failed to save chat: {e}")

    return QueryResponse(
        answer=answer_text,
        sources=sources_list
    )

@app.get("/chats/{chat_id}")
def get_chats_for_session(chat_id: str, current_user: str = Depends(get_current_user)):
    try:
        chats = list(chats_collection.find({"username": current_user, "chat_id": chat_id}).sort("timestamp", 1))
        # Format for frontend
        formatted_chats = []
        for c in chats:
            # User question
            formatted_chats.append({
                "role": "user",
                "text": c.get("question", "")
            })
            # Bot answer
            formatted_chats.append({
                "role": "bot",
                "text": c.get("answer", ""),
                "sources": c.get("sources", [])
            })
        return formatted_chats
    except Exception as e:
        logger.error(f"Error fetching chats: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch chat history")


# ---- Chat Sessions ----
@app.get("/chat-sessions")
def get_chat_sessions(current_user: str = Depends(get_current_user)):
    try:
        sessions = list(chat_sessions_collection.find({"username": current_user}).sort("created_at", -1))
        formatted_sessions = []
        for s in sessions:
            formatted_sessions.append({
                "chat_id": s.get("chat_id"),
                "filename": s.get("filename"),
                "is_starred": s.get("is_starred", False),
                "created_at": s.get("created_at").isoformat() if s.get("created_at") else None
            })
        return {
            "sessions": formatted_sessions,
            "count": len(formatted_sessions),
            "max": 10,
            "remaining": max(0, 10 - len(formatted_sessions))
        }
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch chat sessions")

@app.post("/chat-sessions")
def create_chat_session(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    # Check limit of 10
    existing_count = chat_sessions_collection.count_documents({"username": current_user})
    if existing_count >= 10:
        raise HTTPException(status_code=400, detail="Maximum limit of 10 chat sessions reached.")

    user_files_dir = os.path.join("data", "user_files", current_user)
    os.makedirs(user_files_dir, exist_ok=True)

    file_location = os.path.join(user_files_dir, file.filename)
    
    # Save file
    try:
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file to disk.")

    # Run RAG indexing
    user_output_dir = os.path.join("data", "user_dataset", current_user)
    user_vector_db_dir = os.path.join("data", "user_vector_db", current_user)
    try:
        run_pipeline(files_dir=user_files_dir, output_dir=user_output_dir)
        run_ingest(dataset_dir=user_output_dir, vector_db_dir=user_vector_db_dir)
    except Exception as e:
        logger.error(f"Error processing user file: {e}")
        # Attempt to clean up file if processing fails
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail="Error processing file in index.")

    # Create session document
    chat_id = str(uuid.uuid4())
    session_doc = {
        "chat_id": chat_id,
        "username": current_user,
        "filename": file.filename,
        "is_starred": False,
        "created_at": datetime.utcnow()
    }
    try:
        chat_sessions_collection.insert_one(session_doc)
    except Exception as e:
        logger.error(f"Error saving session: {e}")
        raise HTTPException(status_code=500, detail="Could not save chat session to database")

    return {
        "status": "ok",
        "chat_id": chat_id,
        "filename": file.filename,
        "created_at": session_doc["created_at"].isoformat()
    }

@app.delete("/chat-sessions/{chat_id}")
def delete_chat_session(chat_id: str, current_user: str = Depends(get_current_user)):
    # Find the session
    session = chat_sessions_collection.find_one({"chat_id": chat_id, "username": current_user})
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    filename = session.get("filename")

    # 1. Delete session from MongoDB
    try:
        chat_sessions_collection.delete_one({"chat_id": chat_id, "username": current_user})
    except Exception as e:
        logger.error(f"Error deleting session doc: {e}")
        raise HTTPException(status_code=500, detail="Could not delete chat session.")

    # 2. Delete messages for this session
    try:
        chats_collection.delete_many({"chat_id": chat_id, "username": current_user})
    except Exception as e:
        logger.error(f"Error deleting chat messages: {e}")

    # 3. Handle file deletion if no other chat session uses this exact filename
    sibling_session = chat_sessions_collection.find_one({"filename": filename, "username": current_user})
    if not sibling_session:
        user_files_dir = os.path.join("data", "user_files", current_user)
        file_path = os.path.join(user_files_dir, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error removing file: {e}")

    # 4. Rebuild index (if no sessions remain, purge DB files, otherwise rebuild)
    user_output_dir = os.path.join("data", "user_dataset", current_user)
    user_vector_db_dir = os.path.join("data", "user_vector_db", current_user)
    user_files_dir = os.path.join("data", "user_files", current_user)

    remaining_sessions_count = chat_sessions_collection.count_documents({"username": current_user})
    if remaining_sessions_count == 0:
        # Purge local DB index files
        if os.path.exists(os.path.join(user_vector_db_dir, "index_local.bin")):
            os.remove(os.path.join(user_vector_db_dir, "index_local.bin"))
        if os.path.exists(os.path.join(user_vector_db_dir, "faiss_store.pkl")):
            os.remove(os.path.join(user_vector_db_dir, "faiss_store.pkl"))
        if os.path.exists(os.path.join(user_output_dir, "chunks.json")):
            os.remove(os.path.join(user_output_dir, "chunks.json"))
    else:
        try:
            run_pipeline(files_dir=user_files_dir, output_dir=user_output_dir)
            run_ingest(dataset_dir=user_output_dir, vector_db_dir=user_vector_db_dir)
        except Exception as e:
            logger.error(f"Error rebuilding database: {e}")

    return {"status": "ok", "message": "Chat session and file deleted successfully."}


@app.put("/chat-sessions/{chat_id}/star")
def toggle_star_chat_session(chat_id: str, current_user: str = Depends(get_current_user)):
    try:
        session = chat_sessions_collection.find_one({"chat_id": chat_id, "username": current_user})
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
        
        current_starred = session.get("is_starred", False)
        new_starred = not current_starred
        
        chat_sessions_collection.update_one(
            {"chat_id": chat_id, "username": current_user},
            {"$set": {"is_starred": new_starred}}
        )
        return {
            "status": "ok",
            "chat_id": chat_id,
            "is_starred": new_starred
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error toggling star session: {e}")
        raise HTTPException(status_code=500, detail="Could not toggle star status")


# ---- Search ----
@app.post("/search", response_model=SearchResponse)
def search_docs(req: SearchRequest):
    logger.info(f"[SEARCH] {req.query}")
    docs = search_documents(req.query, req.filters) or []
    results = []
    for i, doc in enumerate(docs, 1):
        results.append(SearchResult(
            id=str(doc.get("id", f"doc-{i}")),
            title=doc.get("title", "Untitled"),
            chunk=doc.get("chunk", ""),
            similarity=float(doc.get("similarity", 0.0)),
            source=doc.get("source", "unknown"),
            page=int(doc.get("page", 0)),
            metadata=doc.get("metadata", {}),
        ))
    return SearchResponse(results=results)

@app.post("/predict")
def predict(req: SearchRequest):
    docs = search_documents(req.query, req.filters) or []
    return docs

# ---- Full Rebuild ----
@app.post("/ingest")
def ingest(current_user: str = Depends(get_current_user)):
    logger.info(f"[INGEST] Full rebuild triggered for user {current_user}")
    
    user_files_dir = os.path.join("data", "user_files", current_user)
    user_output_dir = os.path.join("data", "user_dataset", current_user)
    user_vector_db_dir = os.path.join("data", "user_vector_db", current_user)
    
    os.makedirs(user_files_dir, exist_ok=True)
    
    try:
        run_pipeline(files_dir=user_files_dir, output_dir=user_output_dir)
        run_ingest(dataset_dir=user_output_dir, vector_db_dir=user_vector_db_dir)
        return {"status": "ok", "message": "User files processed and embeddings rebuilt"}
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI backend started!")

@app.get("/user-files")
def get_user_files(current_user: str = Depends(get_current_user)):
    user_files_dir = os.path.join("data", "user_files", current_user)
    if not os.path.exists(user_files_dir):
        return {"files": [], "count": 0, "max": 10, "remaining": 10}
        
    files = os.listdir(user_files_dir)
    return {
        "files": files,
        "count": len(files),
        "max": 10,
        "remaining": max(0, 10 - len(files))
    }

@app.delete("/user-files/{filename}")
def delete_user_file(filename: str, current_user: str = Depends(get_current_user)):
    user_files_dir = os.path.join("data", "user_files", current_user)
    file_path = os.path.join(user_files_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
        
    try:
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Error deleting file.")
        
    user_output_dir = os.path.join("data", "user_dataset", current_user)
    user_vector_db_dir = os.path.join("data", "user_vector_db", current_user)
    
    existing_files = os.listdir(user_files_dir)
    if len(existing_files) == 0:
        if os.path.exists(os.path.join(user_vector_db_dir, "index_local.bin")):
            os.remove(os.path.join(user_vector_db_dir, "index_local.bin"))
        if os.path.exists(os.path.join(user_vector_db_dir, "faiss_store.pkl")):
            os.remove(os.path.join(user_vector_db_dir, "faiss_store.pkl"))
        if os.path.exists(os.path.join(user_output_dir, "chunks.json")):
            os.remove(os.path.join(user_output_dir, "chunks.json"))
    else:
        try:
            run_pipeline(files_dir=user_files_dir, output_dir=user_output_dir)
            run_ingest(dataset_dir=user_output_dir, vector_db_dir=user_vector_db_dir)
        except Exception as e:
            logger.error(f"Error rebuilding database after deletion: {e}")
            
    return {"status": "ok", "message": "File deleted."}

@app.post("/upload")
def upload_file(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    user_files_dir = os.path.join("data", "user_files", current_user)
    os.makedirs(user_files_dir, exist_ok=True)
    
    existing_files = os.listdir(user_files_dir)
    if len(existing_files) >= 10:
        raise HTTPException(status_code=400, detail="Maximum limit of 10 files reached.")
        
    file_location = os.path.join(user_files_dir, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    user_output_dir = os.path.join("data", "user_dataset", current_user)
    user_vector_db_dir = os.path.join("data", "user_vector_db", current_user)
    
    try:
        run_pipeline(files_dir=user_files_dir, output_dir=user_output_dir)
        run_ingest(dataset_dir=user_output_dir, vector_db_dir=user_vector_db_dir)
    except Exception as e:
        logger.error(f"Error processing user file: {e}")
        raise HTTPException(status_code=500, detail="Error processing file.")
        
    return {"status": "ok", "message": "File uploaded and processed."}

from fastapi.responses import FileResponse, HTMLResponse
from src.pipeline import extract_text_from_file

@app.get("/user-files/{filename}/download")
def download_user_file(filename: str, current_user: str = Depends(get_current_user)):
    user_files_dir = os.path.join("data", "user_files", current_user)
    file_path = os.path.join(user_files_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path)

@app.get("/user-files/{filename}/view")
def view_user_file(filename: str, current_user: str = Depends(get_current_user)):
    user_files_dir = os.path.join("data", "user_files", current_user)
    file_path = os.path.join(user_files_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
        
    if filename.lower().endswith(".pdf"):
        return FileResponse(file_path)
    else:
        text_content = extract_text_from_file(file_path)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{filename}</title>
            <style>
                body {{
                    background-color: white !important;
                    color: black !important;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 24px;
                    margin: 0;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-size: 14px;
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body>{text_content}</body>
        </html>
        """
        return HTMLResponse(content=html_content)

# ---- Comments ----
@app.get("/comments")
def get_comments():
    try:
        comments = list(comments_collection.find().sort("timestamp", -1))
        # Format for frontend
        formatted_comments = []
        for c in comments:
            formatted_comments.append({
                "id": str(c["_id"]),
                "username": c.get("username", "Anonymous"),
                "text": c.get("text", ""),
                "timestamp": c.get("timestamp").isoformat() if c.get("timestamp") else None
            })
        return formatted_comments
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch comments")

@app.post("/comments")
def post_comment(req: CommentRequest, current_user: str = Depends(get_current_user)):
    comment_doc = {
        "username": current_user,
        "text": req.text,
        "timestamp": datetime.utcnow()
    }
    try:
        comments_collection.insert_one(comment_doc)
        return {"status": "ok", "message": "Comment posted successfully"}
    except Exception as e:
        logger.error(f"Error posting comment: {e}")
        raise HTTPException(status_code=500, detail="Could not post comment")

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: str, current_user: str = Depends(get_current_user)):
    try:
        obj_id = ObjectId(comment_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid comment ID")
        
    comment = comments_collection.find_one({"_id": obj_id})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if comment.get("username") != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
    try:
        comments_collection.delete_one({"_id": obj_id})
        return {"status": "ok", "message": "Comment deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting comment: {e}")
        raise HTTPException(status_code=500, detail="Could not delete comment")

