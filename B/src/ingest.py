import os
import pickle
import json
import hashlib
from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REAL_DATASET_DIR = os.path.join(DATA_DIR, "real_dataset")
VECTOR_DB_DIR = os.path.join(DATA_DIR, "vector_db")

os.makedirs(VECTOR_DB_DIR, exist_ok=True)

FAISS_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "index_local.bin")
FAISS_STORE_PATH = os.path.join(VECTOR_DB_DIR, "faiss_store.pkl")

EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"

# ----------------------------
# Linking logic (merged here)
# ----------------------------
def _doc_id_from_chunk(chunk: Dict[str, Any]) -> str:
    src = chunk.get("original_source") or chunk.get("source") or ""
    return os.path.basename(src)

def _merge_metadata(md_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    keys = {k for md in md_list for k in (md or {}).keys()}
    for k in keys:
        for md in md_list:
            v = (md or {}).get(k)
            if isinstance(v, str):
                v = v.strip()
            if v:
                out[k] = v
                break
        if k not in out:
            out[k] = ""
    return out

def build_document_graph(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    doc_chunks: Dict[str, List[Dict[str, Any]]] = {}
    for ch in chunks:
        did = _doc_id_from_chunk(ch)
        if not did:
            continue
        doc_chunks.setdefault(did, []).append(ch)

    documents: Dict[str, Dict[str, Any]] = {}
    for did, group in doc_chunks.items():
        md_list = [c.get("metadata", {}) for c in group]
        merged = _merge_metadata(md_list)
        merged["document_id"] = did
        documents[did] = merged

    def norm(s: Any) -> str:
        return (s or "").strip().lower()

    conventions, offers = [], []
    for did, md in documents.items():
        cat = norm(md.get("category"))
        if cat == "convention":
            conventions.append(did)
        elif cat in ("offres", "offres en arabe"):
            offers.append(did)

    conventions.sort()
    offers.sort()

    MAX_LINKS_PER_CONVENTION = 5
    links: List[Dict[str, Any]] = []

    for c_id in conventions:
        md_c = documents[c_id]
        partner_c = norm(md_c.get("partner"))
        offer_c = norm(md_c.get("offer_type"))
        if not partner_c:
            continue

        candidates: List[str] = []
        for o_id in offers:
            md_o = documents[o_id]
            partner_o = norm(md_o.get("partner"))
            offer_o = norm(md_o.get("offer_type"))
            if partner_o != partner_c:
                continue
            if offer_c and offer_o and offer_c != offer_o:
                continue
            candidates.append(o_id)

        candidates.sort()
        for o_id in candidates[:MAX_LINKS_PER_CONVENTION]:
            links.append({"source": c_id, "target": o_id, "relation": "offer_convention_link"})

    return {"documents": documents, "links": links}

def integrate_graph_into_chunks(chunks: List[Dict[str, Any]], graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    adj: Dict[str, set] = {}
    for link in graph.get("links", []):
        s, t = link.get("source"), link.get("target")
        if not s or not t:
            continue
        adj.setdefault(s, set()).add(t)
        adj.setdefault(t, set()).add(s)

    out: List[Dict[str, Any]] = []
    for ch in chunks:
        did = _doc_id_from_chunk(ch)
        new_ch = dict(ch)
        new_ch["links"] = sorted(adj.get(did, set()))
        out.append(new_ch)
    return out

# ----------------------------
# Load + enrich corpus
# ----------------------------
def build_corpus(dataset_dir: str = REAL_DATASET_DIR) -> List[Dict[str, Any]]:
    dataset_path = os.path.join(dataset_dir, "chunks.json")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"chunks.json not found at {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    graph = build_document_graph(chunks)
    enriched_chunks = integrate_graph_into_chunks(chunks, graph)

    seen_hashes = set()
    corpus: List[Dict[str, Any]] = []
    for i, c in enumerate(enriched_chunks):
        text = c.get("text", "")
        h = c.get("hash")
        if not h:
            h = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
            c["hash"] = h
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        c["id"] = i
        corpus.append(c)

    return corpus

# ----------------------------
# Embed corpus
# ----------------------------
def embed_corpus(corpus: List[Dict[str, Any]]) -> np.ndarray:
    texts = [c["text"] for c in corpus]
    from .retriever import get_embedding_model
    model = get_embedding_model()
    
    # Use a smaller batch size to prevent OOM memory spikes during PyTorch forward pass on CPU
    vectors = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    
    # Force garbage collection to release memory immediately
    import gc
    gc.collect()
    
    return np.array(vectors, dtype="float32")

# ----------------------------
# Save FAISS index + metadata
# ----------------------------
def save_faiss_index(vectors: np.ndarray, corpus: List[Dict[str, Any]], index_path: str = FAISS_INDEX_PATH, store_path: str = FAISS_STORE_PATH):
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity
    index.add(vectors)

    faiss.write_index(index, index_path)

    store = {
        "ids": [c["id"] for c in corpus],
        "texts": [c["text"] for c in corpus],
        "sources": [c.get("filename", "") for c in corpus],
        "original_sources": [c.get("original_source", "") for c in corpus],
        "pages": [c.get("page", 0) for c in corpus],
        "metadata": [c.get("metadata", {}) for c in corpus],
        "hashes": [c.get("hash", "") for c in corpus],
        "links": [c.get("links", []) for c in corpus],  # ✅ include related doc links
    }
    with open(store_path, "wb") as fh:
        pickle.dump(store, fh)

# ----------------------------
# Main
# ----------------------------
def run_ingest(dataset_dir: str = REAL_DATASET_DIR, vector_db_dir: str = VECTOR_DB_DIR):
    os.makedirs(vector_db_dir, exist_ok=True)
    index_path = os.path.join(vector_db_dir, "index_local.bin")
    store_path = os.path.join(vector_db_dir, "faiss_store.pkl")

    print(f"Loading chunks from {dataset_dir}...")
    try:
        corpus = build_corpus(dataset_dir)
    except FileNotFoundError:
        print("No chunks found. Skipping ingest.")
        return
    print(f"Total chunks: {len(corpus)}")

    if len(corpus) == 0:
        print("Empty corpus. Skipping.")
        return

    print("Embedding corpus...")
    vectors = embed_corpus(corpus)

    print("Saving FAISS index and store...")
    save_faiss_index(vectors, corpus, index_path, store_path)

    print(f"✅ Done. Index saved to {index_path}")
    print(f"✅ Metadata saved to {store_path}")

def main():
    run_ingest()

if __name__ == "__main__":
    main()
