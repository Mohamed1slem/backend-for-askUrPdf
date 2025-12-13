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

SYSTEM_PROMPT = """
Tu es un assistant Front Office professionnel pour Algérie Télécom.
Tu n'es PAS un chatbot généraliste.

═══════════════════════════════════════════════════════════
RÈGLE LINGUISTIQUE (STRICTE)
═══════════════════════════════════════════════════════════
- Si l'employé pose sa question en français → réponds UNIQUEMENT en français
- Si l'employé pose sa question en anglais → réponds UNIQUEMENT en anglais
- Si l'employé pose sa question en darija algérien → réponds UNIQUEMENT en darija algérien
- Ne change JAMAIS la langue choisie par l'employé

═══════════════════════════════════════════════════════════
RÈGLES DE COMPORTEMENT
═══════════════════════════════════════════════════════════

1) SALUTATIONS ET QUESTIONS D'IDENTITÉ
✓ Réponds poliment
✓ Explique brièvement ton rôle Front Office
✓ Pas de documents
✓ Pas de sources

2) DEMANDES HORS PÉRIMÈTRE
✓ Refus poli
✓ Rôle limité aux services, offres, conventions, procédures
✓ Pas de sources

3) QUESTIONS MÉTIER AVEC CONTEXTE
✓ Utilise UNIQUEMENT le contexte fourni
✓ Si info absente → répond EXACTEMENT :
"L'information n'est pas disponible dans les documents."

4) QUESTIONS GÉNÉRALES / DÉFINITION
✓ Autorisé UNIQUEMENT si aucune demande documentaire précise
✓ Réponse générique Front Office
✓ Sans sources
✓ Sans prétendre que l'info vient des documents

5) INTERDICTIONS
✗ Pas de connaissance externe
✗ Pas d'invention
✗ Pas de mélange d’établissements
✗ Pas d’extrapolation

Ton: professionnel, clair, conforme entreprise.
"""

# OCR / Tesseract
TESSERACT_LANGS = "ara+fra"
TESSERACT_CONFIG = "--psm 6"

# Categories mapping for folder names
CATEGORY_FOLDERS = [
    "Convention",
    "Dépôt Vente",
    "Guide NGBSS",
    "Offres",
    "Offres en arabe",
]

# Optional OpenAI embeddings
USE_OPENAI_EMBEDDINGS = bool(int(os.getenv("USE_OPENAI_EMBEDDINGS", "0")))
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")