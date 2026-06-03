import os

# ----------------------------
# BASE PATHS
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Where raw files are placed before processing
FILES_DIR = os.path.join(DATA_DIR, "files")

# Where cleaned/enriched chunks are stored
REAL_DATASET_DIR = os.path.join(DATA_DIR, "real_dataset")

# Where FAISS index + metadata store are saved
VECTOR_DB_DIR = os.path.join(DATA_DIR, "vector_db")

# ----------------------------
# CHUNKING PARAMETERS
# ----------------------------
# Default chunk size (characters)
CHUNK_SIZE = 500

# Default overlap between chunks (characters)
CHUNK_OVERLAP = 100

# ----------------------------
# OCR / TESSERACT SETTINGS
# ----------------------------
# Languages for OCR (Arabic + French + English)
TESSERACT_LANGS = "ara+fra+eng"

# Tesseract config string
TESSERACT_CONFIG = "--psm 6"

# ----------------------------
# CATEGORY FOLDERS
# ----------------------------
# Used to infer document category from file path
CATEGORY_FOLDERS = [
    "conventions",
    "offres",
    "offres en arabe",
    "guides",
    "depot_vente",
]
# ----------------------------
# Chatbot / LLM settings
# ----------------------------
SYSTEM_PROMPT = """You are an AI assistant that answers questions based on retrieved documents.
Always cite sources clearly and keep answers concise and accurate.
"""
OPENAI_MODEL = "llama-3.3-70b-versatile"
# ----------------------------
# EMBEDDING MODEL
# ----------------------------
# SentenceTransformers multilingual model
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"

# ----------------------------
# FAISS INDEX PATHS
# ----------------------------
FAISS_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "index_local.bin")
FAISS_STORE_PATH = os.path.join(VECTOR_DB_DIR, "faiss_store.pkl")

TOP_K = 5  # default number of results to return
