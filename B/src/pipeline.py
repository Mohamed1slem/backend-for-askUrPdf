import os
import io
from typing import List, Dict, Any, Tuple
import hashlib
import re

from PIL import Image
import pytesseract
from pdfminer.high_level import extract_text as pdf_extract_text
import docx2txt
from docx import Document as DocxDocument
import arabic_reshaper
from bidi.algorithm import get_display
from unidecode import unidecode
from .config import BASE_DIR

from .config import (
    CHUNK_SIZE, CHUNK_OVERLAP, TESSERACT_LANGS, TESSERACT_CONFIG, CATEGORY_FOLDERS
)


def is_scanned_pdf(pdf_path: str) -> bool:
    # Heuristic: try extracting text; if nearly empty, assume scanned
    try:
        txt = pdf_extract_text(pdf_path) or ""
        return len(txt.strip()) < 30
    except Exception:
        return True


def extract_pdf_pages(pdf_path: str) -> List[Tuple[int, str]]:
    """Return list of (page_number starting at 1, text) using PyMuPDF; OCR page if needed."""
    pages: List[Tuple[int, str]] = []
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            if len(text.strip()) < 10:  # likely scanned
                pix = page.get_pixmap(dpi=220)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(img, lang=TESSERACT_LANGS, config=TESSERACT_CONFIG) or ""
            pages.append((i, text))
        return pages
    except Exception:
        # Fallback: no page granularity
        whole = pdf_extract_text(pdf_path) or ""
        return [(1, whole)]


def extract_text_from_file(path: str) -> Tuple[str, Dict[str, Any]]:
    fname = os.path.basename(path)
    ext = fname.lower().split('.')[-1]
    meta = {
        "source": fname,
        "category": infer_category_from_path(path),
    }
    if ext == "pdf":
        # For callers that need whole text only (not used in chunk builder now)
        pages = extract_pdf_pages(path)
        text = "\n".join(t for _, t in pages)
        return text, meta
    elif ext in ("doc", "docx"):
        try:
            text = docx2txt.process(path) or ""
        except Exception:
            # Fallback using python-docx for docx
            if ext == "docx":
                d = DocxDocument(path)
                text = "\n".join(p.text for p in d.paragraphs)
            else:
                text = ""
        return text, meta
    else:
        # Unsupported: return empty
        return "", meta


def clean_text(raw: str) -> str:
    if not raw:
        return ""
    s = raw
    # Remove repeated sequences (simple heuristic)
    lines = [l.strip() for l in s.splitlines()]
    dedup = []
    seen = set()
    for l in lines:
        k = l.lower()
        if len(k) > 0 and k not in seen:
            dedup.append(l)
            seen.add(k)
    s = "\n".join(dedup)

    # Normalize Arabic shaping and direction via arabic_reshaper + bidi
    try:
        reshaped = arabic_reshaper.reshape(s)
        s = get_display(reshaped)
    except Exception:
        pass

    # Collapse spaces, remove headers/footers heuristically
    s = "\n".join([l for l in s.splitlines() if len(l.strip()) > 0])
    return s


def sentence_split(text: str) -> List[str]:
    # Lightweight sentence splitter: split on punctuation.
    import re
    parts = re.split(r"(?<=[\.!?\u061F])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _adjust_chunk_params(sentences: List[str], base_size: int, base_overlap: int) -> Tuple[int, int]:
    """Dynamically adjust chunk size/overlap when sentences are too long/short."""
    if not sentences:
        return base_size, base_overlap
    avg_len = sum(len(s) for s in sentences) / max(len(sentences), 1)
    size = base_size
    overlap = base_overlap
    if avg_len > base_size * 0.8:
        size = int(base_size * 1.3)
        overlap = int(base_overlap * 0.6)
    elif avg_len < base_size * 0.25:
        size = int(base_size * 0.8)
        overlap = int(base_overlap * 1.2)
    return max(300, min(size, 1200)), max(30, min(overlap, 300))


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []
    sentences = sentence_split(text)
    # dynamic adjust
    size, overlap = _adjust_chunk_params(sentences, size, overlap)
    chunks: List[str] = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 1 <= size:
            current = (current + " " + s).strip()
        else:
            if current:
                chunks.append(current)
            # Overlap by sentences (approx via tail characters)
            tail = current[-overlap:] if current else ""
            current = (tail + " " + s).strip()
    if current:
        chunks.append(current)
    return chunks


def infer_category_from_path(path: str) -> str:
    # Find top-level folder as category
    rel = path
    for cat in CATEGORY_FOLDERS:
        if cat in path:
            return cat
    return ""


def extract_metadata(path: str, text: str) -> Dict[str, Any]:
    """Heuristic metadata extraction from folder, filename, and text patterns."""
    filename = os.path.basename(path)
    category = infer_category_from_path(path)
    partner = ""
    offer_type = ""
    sector = ""

    base = filename.lower()
    # Keyword dictionaries (Arabic + French)
    partner_dict = [
        "algérie télécom", "algerie telecom", "ekoteb", "classateck", "classatec", "اتصالات الجزائر"
    ]
    offer_dict = [
        "ligne temporaire", "idooom 4g lte", "idoom 4g lte", "recharge", "fibre", "adsl", "vdsl",
        "entreprise", "premium"
    ]
    sector_dict = [
        "education", "éducation", "telecom", "télécom", "commercial", "commerce", "banque", "santé", "industrie"
    ]

    # Regex patterns for headings on first page
    head = (text or "")[:1000]
    head_l = head.lower()
    heading_patterns = {
        "partner": [
            r"(?:partenaire|partner|شريك)[:\s-]*([A-Za-zÀ-ÿ\u0600-\u06FF ]{3,})",
            r"(?:algérie télécom|اتصالات الجزائر)"
        ],
        "offer_type": [
            r"(?:offre|offer|عرض)[:\s-]*([A-Za-z0-9À-ÿ\u0600-\u06FF \-]{3,})",
            r"(?:ligne temporaire|idoom 4g lte|recharge|fibre|adsl|vdsl)"
        ],
        "sector": [
            r"(?:secteur|sector|قطاع)[:\s-]*([A-Za-zÀ-ÿ\u0600-\u06FF ]{3,})",
            r"(?:education|éducation|telecom|télécom|commercial|banque|santé|industrie)"
        ]
    }

    # Signals from filename
    for p in partner_dict:
        if p in base and not partner:
            partner = "Algérie Télécom" if "algérie" in p or "اتصالات" in p else p.title()
    for o in offer_dict:
        if o in base and not offer_type:
            offer_type = o.title()
    for s in sector_dict:
        if s in base and not sector:
            sector = s.capitalize()

    # Signals from headings
    for pat in heading_patterns["partner"]:
        m = re.search(pat, head_l)
        if m and not partner:
            partner = (m.group(1).strip() if m.groups() else m.group(0)).title()
            break
    for pat in heading_patterns["offer_type"]:
        m = re.search(pat, head_l)
        if m and not offer_type:
            offer_type = (m.group(1).strip() if m.groups() else m.group(0)).title()
            break
    for pat in heading_patterns["sector"]:
        m = re.search(pat, head_l)
        if m and not sector:
            sector = (m.group(1).strip() if m.groups() else m.group(0)).capitalize()
            break

    return {
        "category": category,
        "partner": partner,
        "offer_type": offer_type,
        "sector": sector,
    }


def build_chunks_for_file(path: str) -> List[Dict[str, Any]]:
    ext = os.path.basename(path).lower().split(".")[-1]
    out: List[Dict[str, Any]] = []
    if ext == "pdf":
        pages = extract_pdf_pages(path)
        for page_num, page_text in pages:
            clean = clean_text(page_text)
            # metadata per page
            md = extract_metadata(path, clean)
            pieces = chunk_text(clean)
            for i, ch in enumerate(pieces):
                chunk_hash = hashlib.sha256(ch.encode("utf-8", errors="ignore")).hexdigest()
                out.append({
                    "id": f"{os.path.basename(path)}_p{page_num}_chunk{i}",
                    "text": ch,
                    "source": f"{os.path.basename(path)}_chunk{i}.txt",
                    "original_source": path,
                    "page": page_num,
                    "metadata": md,
                    "hash": chunk_hash,
                })
    else:
        # DOCX and others handled as one flow (page unknown)
        text, _ = extract_text_from_file(path)
        clean = clean_text(text)
        md = extract_metadata(path, clean)
        pieces = chunk_text(clean)
        for i, ch in enumerate(pieces):
            chunk_hash = hashlib.sha256(ch.encode("utf-8", errors="ignore")).hexdigest()
            out.append({
                "id": f"{os.path.basename(path)}_chunk{i}",
                "text": ch,
                "source": f"{os.path.basename(path)}_chunk{i}.txt",
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

def build_chunks_with_links(root: str) -> List[Dict[str, Any]]:
    """
    Build all chunks from files under root, then construct a document graph
    and integrate linked document ids into each chunk.

    This function does not modify extraction/cleaning/chunking/metadata logic.
    It only orchestrates a deterministic linking step after chunk generation.
    """
    from .linking import build_document_graph, integrate_graph_into_chunks

    all_chunks: List[Dict[str, Any]] = []
    for path in load_all_files(root):
        all_chunks += build_chunks_for_file(path)

    graph = build_document_graph(all_chunks)
    enriched_chunks = integrate_graph_into_chunks(all_chunks, graph)

    final_chunks: List[Dict[str, Any]] = []
    for ch in enriched_chunks:
        original = ch.get("original_source") or ch.get("source") or ""
        link_path = ""

        if original:
            if os.path.isabs(original):
                try:
                    link_path = os.path.relpath(original, BASE_DIR)
                except Exception:
                    link_path = original
            else:
                link_path = os.path.normpath(original)

        final_chunks.append({
            "content": ch.get("text", ""),
            "metadata": ch.get("metadata", {}),
            "source_links": [link_path] if link_path else [],
            # هذا هو الربط الحقيقي بين الوثائق (Phase 3)
            "related_links": ch.get("links", []),
        })

    return final_chunks

