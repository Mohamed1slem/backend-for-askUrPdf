import os
import requests
from dotenv import load_dotenv

from .config import SYSTEM_PROMPT, DEEPSEEK_API_URL, DEEPSEEK_MODEL
from .retriever import Retriever

load_dotenv()

DEBUG_MODE = False
MIN_SIMILARITY = 60.0

def format_context(chunks):
    """
    Formats the retrieved document chunks into a context string for the LLM.
    """
    lines = []
    for c in chunks:
        sim = c.get("boosted_similarity", c["similarity"])
        chunk_label = ""
        if "_chunk" in c["source"]:
            try:
                chunk_label = f" | {c['source'].split('_chunk')[-1].replace('.txt','')}"
            except Exception:
                chunk_label = ""
        lines.append(f"[Source: {c['source']} | Original: {c.get('original_source','N/A')} | Similarity: {sim}%]")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)

def answer_query(query: str):
    """
    Main function to answer a user query using retrieved document chunks
    and the DeepSeek API.
    """
    print("Received query:", query)

    # 1. Retrieve relevant document chunks
    retriever = Retriever()
    chunks = retriever.search(query, top_k=10)
    # Filter by minimum similarity
    chunks = [c for c in chunks if c.get("boosted_similarity", c["similarity"]) >= MIN_SIMILARITY]
    chunks = chunks[:5]

    print("Retrieved sources:", [(c["source"], c.get("boosted_similarity", c["similarity"])) for c in chunks])
    context = format_context(chunks)
    print(f"Retrieved {len(chunks)} chunks for context.")

    # 2. Prepare prompt for DeepSeek
    user_prompt = (
        f"Question: {query}\n\n"
        f"Context:\n{context}\n\n"
        "Answer using only the context above. "
        "If unsure, say you don't have sufficient information."
    )

    # 3. Get API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {
            "answer": "DEEPSEEK_API_KEY not set. Please configure your environment.",
            "sources": [f"{c['source']} ({c.get('boosted_similarity', c['similarity'])}%)" for c in chunks]
        }

    # 4. Debug mode (optional)
    if DEBUG_MODE:
        return {
            "answer": f"[DEBUG] Retrieved {len(chunks)} chunks. Top source: {chunks[0]['source'] if chunks else 'None'}",
            "sources": [f"{c['source']} ({c.get('boosted_similarity', c['similarity'])}%)" for c in chunks]
        }

    # 5. Call DeepSeek API (non-streaming)
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    answer = ""
    try:
        print("➡️ Requesting response from DeepSeek API...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        # Extract answer from response
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        print("✅ Response received:", answer[:100], "..." if len(answer) > 100 else "")
    except Exception as e:
        print("❌ Request failed:", e)
        answer = "⚠️ DeepSeek request failed. Showing sources instead."

    # 6. Prepare sources
    sources = [f"{c['source']} ({c.get('boosted_similarity', c['similarity'])}%)" for c in chunks]

    return {"answer": answer, "sources": sources}
