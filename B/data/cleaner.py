import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from docx import Document

# ----------------------------
# SETTINGS
# ----------------------------
FILES_DIR = r"C:\Users\user\Desktop\RAG bot\B\data\files"
OUTPUT_DIR = r"C:\Users\user\Desktop\RAG bot\B\data\real_dataset"
CHUNK_SIZE = 250
LANGS = "ara+fra+eng"
MAX_WORKERS = 4

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------
# TEXT CLEANING
# ----------------------------
def clean_text(text: str) -> str:
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'[^\S\r\n]+', ' ', text)
    text = re.sub(r'[|_]{3,}', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    # Arabic normalization
    text = text.replace('ـ', '')
    text = re.sub('[إأآ]', 'ا', text)
    text = text.replace('ى', 'ي')
    # Keep "ة" intact unless you want normalization
    lines = [line for line in text.splitlines() if line.strip()]
    return '\n'.join(lines).strip()

# ----------------------------
# DOCX EXTRACTION (python-docx)
# ----------------------------
def extract_docx(file_path):
    try:
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return clean_text(text)
    except Exception as e:
        print(f"❌ DOCX error: {file_path} → {e}")
        return ""

# ----------------------------
# PDF EXTRACTION
# ----------------------------
def extract_pdf(file_path):
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            page_text = page.get_text("text")
            if page_text.strip():
                text += page_text
            else:
                # OCR only if page has no text
                pix = page.get_pixmap(dpi=200)
                ocr_text = pytesseract.image_to_string(pix.tobybytes(), lang=LANGS)
                text += ocr_text
        doc.close()
    except Exception as e:
        print(f"⚠ PDF extraction failed: {file_path} → {e}")
    return clean_text(text)

# ----------------------------
# CHUNKING (generator style)
# ----------------------------
def chunk_text(text, size):
    words = text.split()
    current, length = [], 0
    for word in words:
        length += len(word) + 1
        if length > size and current:
            yield " ".join(current)
            current, length = [word], len(word) + 1
        else:
            current.append(word)
    if current:
        yield " ".join(current)

# ----------------------------
# PROCESS SINGLE FILE
# ----------------------------
def process_file(filename):
    path = os.path.join(FILES_DIR, filename)
    if not os.path.isfile(path):
        return []

    print(f"📄 Processing: {filename}")
    text = ""

    if filename.lower().endswith(".docx"):
        text = extract_docx(path)
    elif filename.lower().endswith(".pdf"):
        text = extract_pdf(path)
    else:
        print(f"⚠ Skipped unsupported file: {filename}")
        return []

    if not text:
        print(f"⚠ No text extracted from {filename}")
        return []

    chunks = list(chunk_text(text, CHUNK_SIZE))
    dataset = [{"filename": filename, "chunk_id": i, "text": chunk} for i, chunk in enumerate(chunks)]

    # Save full cleaned text to .txt
    out_txt = os.path.join(OUTPUT_DIR, os.path.splitext(filename)[0] + ".txt")
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ {filename}: {len(chunks)} chunks → saved {out_txt}")
    return dataset

# ----------------------------
# MAIN PIPELINE
# ----------------------------
dataset = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(process_file, f) for f in os.listdir(FILES_DIR)]
    for future in as_completed(futures):
        try:
            dataset.extend(future.result())
        except Exception as e:
            print(f"⚠ Worker failed: {e}")

# ----------------------------
# SAVE DATASET (optional JSON)
# ----------------------------
output_file = os.path.join(OUTPUT_DIR, "chunks.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print("\n🎉 DONE")
print(f"📦 Total chunks: {len(dataset)}")
print(f"💾 Saved to: {output_file}")
