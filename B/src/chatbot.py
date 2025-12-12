import os
import requests
from dotenv import load_dotenv

from .config import SYSTEM_PROMPT, DEEPSEEK_API_URL, DEEPSEEK_MODEL
from .retriever import Retriever

load_dotenv()

DEBUG_MODE = False
MIN_SIMILARITY = 60.0

def format_context(chunks):
    lines = []
    for c in chunks:
        sim = c.get("boosted_similarity", c["similarity"])
        chunk_label = ""
        if "_chunk" in c["source"]:
            try:
                chunk_label = f" | {c['source'].split('_chunk')[-1].replace('.txt','')}"
            except Exception:
                chunk_label = ""
        lines.append(f"[Source: {c['source']} | Original: {c['original_source']} | Similarity: {sim}%]")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)

def answer_query(query: str):
    print("Received query:", query)

    retriever = Retriever()
    chunks = retriever.search(query, top_k=10)
    chunks = [c for c in chunks if c.get("boosted_similarity", c["similarity"]) >= MIN_SIMILARITY]
    chunks = chunks[:5]

    print("Retrieved sources:", [(c["source"], c.get("boosted_similarity", c["similarity"])) for c in chunks])
    context = format_context(chunks)
    print(f"Retrieved {len(chunks)} chunks for context.")

    user_prompt = (
        f"Question: {query}\n\n"
        f"Context:\n{context}\n\n"
        "Answer using only the context above. If unsure, say you don't have sufficient information."
    )

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {
            "answer": "DEEPSEEK_API_KEY not set. Please configure your environment.",
            "sources": [f"{c['source']} ({c.get('boosted_similarity', c['similarity'])}%)" for c in chunks]
        }

    if DEBUG_MODE:
        return {
            "answer": f"[DEBUG] Retrieved {len(chunks)} chunks. Top source: {chunks[0]['source'] if chunks else 'None'}",
            "sources": [f"{c['source']} ({c.get('boosted_similarity', c['similarity'])}%)" for c in chunks]
        }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": True  # ✅ enable streaming
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    answer = ""
    try:
        print("➡️ Streaming response from DeepSeek API...")
        with requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, stream=True, timeout=20) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if line and line.startswith("data:"):
                    data = line[len("data:"):].strip()
                    if data == "[DONE]":
                        break
                    try:
                        token = eval(data).get("choices", [{}])[0].get("delta", {}).get("content", "")
                        answer += token
                        print(token, end="", flush=True)  # live printing
                    except Exception:
                        continue
        print("\n✅ Streaming complete.")
    except Exception as e:
        print("❌ Streaming failed, falling back:", e)
        answer = "⚠️ DeepSeek streaming failed. Showing sources instead."

    sources = [f"{c['source']} ({c.get('boosted_similarity', c['similarity'])}%)" for c in chunks]
    return {"answer": answer.strip(), "sources": sources}
