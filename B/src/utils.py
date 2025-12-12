import os
from typing import List, Tuple

def load_text_files(root_dir: str) -> List[Tuple[str, str]]:
    """
    Recursively load .txt files from root_dir and its subfolders.
    Returns list of tuples: (file_path, file_content).
    """
    files = []
    for r, _, f_list in os.walk(root_dir):
        for f in f_list:
            if f.lower().endswith(".txt"):
                p = os.path.join(r, f)
                try:
                    with open(p, "r", encoding="utf-8") as fh:
                        files.append((p, fh.read()))
                except Exception as e:
                    print(f"⚠️ Skipped {p}: {e}")
                    continue
    return files

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into overlapping chunks.
    """
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end >= n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def rel_path_from_base(base_dir: str, full_path: str) -> str:
    """
    Get relative path for metadata.
    """
    try:
        return os.path.relpath(full_path, base_dir)
    except ValueError:
        return full_path
