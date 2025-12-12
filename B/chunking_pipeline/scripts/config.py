# -----------------------
# Folders
# -----------------------
RAW_FOLDER = "RAW"               # Original DOCX/PDF files
CLEAN_TEXT_FOLDER = "CLEAN_TEXT" # Extracted text (from files and images)
CHUNKS_OUTPUT = "CHUNKS_OUTPUT"  # Final JSON chunks

# -----------------------
# Chunking parameters
# -----------------------
CHUNK_SIZE = 500
OVERLAP = 50

# -----------------------
# Embedding model
# -----------------------
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
