import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

FAISS_INDEX_PATH = os.path.join(EMBEDDINGS_DIR, "faiss_index.bin")
FAISS_STORE_PATH = os.path.join(EMBEDDINGS_DIR, "faiss_store.pkl")

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 5

# DeepSeek API
DEEPSEEK_API_URL = "https://api.modelarts-maas.com/v2/chat/completions"
DEEPSEEK_MODEL = "deepseek-v3.1"

SYSTEM_PROMPT = (
    "You are a helpful assistant for answering questions using provided context. "
    "Always base your answer strictly on the given context. If the answer is not "
    "present, say you don't have sufficient information. Keep answers clear and concise."
)

# OCR / Tesseract
TESSERACT_LANGS = "ara+fra"
TESSERACT_CONFIG = "--psm 6"

# Categories mapping for folder names
CATEGORY_FOLDERS = [
    "Convention",
    "Dépot Vente",
    "Guide NGBSS",
    "Offres",
    "Offres en arabe",
]

# Optional OpenAI embeddings
USE_OPENAI_EMBEDDINGS = bool(int(os.getenv("USE_OPENAI_EMBEDDINGS", "0")))
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
