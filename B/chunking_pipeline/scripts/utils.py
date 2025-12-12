import re

# -----------------------
# Text cleaning
# -----------------------
def clean_text(text):
    """
    Remove extra spaces, line breaks, tabs
    """
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -----------------------
# Chunking function
# -----------------------
def split_text_into_chunks(text, chunk_size=500, overlap=50):
    """
    Split text into semantic chunks with overlap
    """
    text = clean_text(text)
    sentences = text.split(". ")
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence.split())
        if current_len + sentence_len > chunk_size:
            chunks.append(". ".join(current_chunk).strip())
            # Keep overlap
            current_chunk = current_chunk[-overlap:] if overlap < len(current_chunk) else current_chunk
            current_len = sum(len(s.split()) for s in current_chunk)
        current_chunk.append(sentence)
        current_len += sentence_len

    if current_chunk:
        chunks.append(". ".join(current_chunk).strip())

    return chunks
