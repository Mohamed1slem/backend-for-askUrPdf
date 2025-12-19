import os
import io
import re
import json
import hashlib
from typing import List, Dict, Any

import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from docx import Document as DocxDocument
import docx2txt
import arabic_reshaper
from bidi.algorithm import get_display

from .config import BASE_DIR, CHUNK_SIZE, CHUNK_OVERLAP, TESSERACT_LANGS, TESSERACT_CONFIG, CATEGORY_FOLDERS

# ----------------------------
# Paths
# ----------------------------
FILES_DIR = os.path.join(BASE_DIR, "data", "files")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "real_dataset")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------
# TEXT CLEANING
# ----------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'[^\S\r\n]+', ' ', text)
    text = re.sub(r'[|_]{3,}', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.replace('ـ', '')
    text = re.sub('[إأآ]', 'ا', text)
    text = text.replace('ى', 'ي')
    lines = [line for line in text.splitlines() if line.strip()]
    s = '\n'.join(lines).strip()

    # Normalize Arabic shaping and direction
    try:
        reshaped = arabic_reshaper.reshape(s)
        s = get_display(reshaped)
    except Exception:
        pass

    return s

# ----------------------------
# FILE EXTRACTION
# ----------------------------
def extract_pdf(file_path: str) -> str:
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            page_text = page.get_text("text")
            if page_text.strip():
                text += page_text
            else:
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img, lang=TESSERACT_LANGS, config=TESSERACT_CONFIG)
                text += ocr_text
        doc.close()
    except Exception as e:
        print(f"⚠ PDF extraction failed: {file_path} → {e}")
    return clean_text(text)

def extract_docx(file_path: str) -> str:
    try:
        text = docx2txt.process(file_path) or ""
        if not text:
            d = DocxDocument(file_path)
            text = "\n".join(p.text for p in d.paragraphs if p.text.strip())
        return clean_text(text)
    except Exception as e:
        print(f"❌ DOCX error: {file_path} → {e}")
        return ""

def extract_text_from_file(path: str) -> str:
    if path.lower().endswith(".pdf"):
        return extract_pdf(path)
    elif path.lower().endswith((".docx", ".doc")):
        return extract_docx(path)
    else:
        return ""

# ----------------------------
# CHUNKING
# ----------------------------
def sentence_split(text: str) -> List[str]:
    parts = re.split(r"(?<=[\.!?\u061F])\s+", text)
    return [p.strip() for p in parts if p.strip()]

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []
    sentences = sentence_split(text)
    chunks: List[str] = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 1 <= size:
            current = (current + " " + s).strip()
        else:
            if current:
                chunks.append(current)
            tail = current[-overlap:] if current else ""
            current = (tail + " " + s).strip()
    if current:
        chunks.append(current)
    return chunks

# ----------------------------
# METADATA EXTRACTION
# ----------------------------
def infer_category_from_path(path: str) -> str:
    for cat in CATEGORY_FOLDERS:
        if cat in path:
            return cat
    return ""

def extract_metadata(path: str, text: str) -> Dict[str, Any]:
    filename = os.path.basename(path)
    category = infer_category_from_path(path)
    return {"category": category}

# ----------------------------
# BUILD CHUNKS
# ----------------------------
def build_chunks_for_file(path: str) -> List[Dict[str, Any]]:
    text = extract_text_from_file(path)
    clean = clean_text(text)
    md = extract_metadata(path, clean)
    pieces = chunk_text(clean)
    out: List[Dict[str, Any]] = []
    for i, ch in enumerate(pieces):
        chunk_hash = hashlib.sha256(ch.encode("utf-8", errors="ignore")).hexdigest()
        out.append({
            "id": f"{os.path.basename(path)}_chunk{i}",
            "text": ch,
            "filename": os.path.basename(path),
            "original_source": path,
            "page": 0,
            "metadata": md,
            "hash": chunk_hash,
        })
    return out

def load_all_files(root: str) -> List[str]:
    paths = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith((".pdf", ".doc", ".docx")):
                paths.append(os.path.join(dirpath, fn))
    return paths

# ----------------------------
# MAIN PIPELINE
# ----------------------------
def main():
    print(f"📂 Scanning files in {FILES_DIR}...")
    all_chunks: List[Dict[str, Any]] = []
    for path in load_all_files(FILES_DIR):
        print(f"📄 Processing: {os.path.basename(path)}")
        all_chunks += build_chunks_for_file(path)

    # Save raw chunks (linking handled in ingest)
    output_file = os.path.join(OUTPUT_DIR, "chunks.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n✅ DONE")
    print(f"📦 Total chunks: {len(all_chunks)}")
    print(f"💾 Saved to: {output_file}")

if __name__ == "__main__":
    main()
