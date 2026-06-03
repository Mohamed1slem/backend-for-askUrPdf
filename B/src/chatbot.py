import os
import re
from dotenv import load_dotenv
from openai import OpenAI

from .config import SYSTEM_PROMPT, OPENAI_MODEL
from .memory import read_memory, write_memory, extract_memory_facts
from .retriever import Retriever, expand_with_related

load_dotenv()

MIN_SIMILARITY = 60.0
FALLBACK_TEXT = "L'information n'est pas disponible dans les documents."

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)
retriever = Retriever()  # ✅ global retriever instance


def detect_language(text: str) -> str:
    text_lower = text.lower()
    if any(word in text_lower for word in ["hello", "hi", "what", "how", "service", "offer", "convention"]):
        return "en"
    if any(word in text_lower for word in ["واش", "كيفاش", "شحال", "علاش", "كاين"]):
        return "darija"
    return "fr"


def format_context(chunks):
    lines = []
    for c in chunks:
        sim = c.get("boosted_similarity", c.get("similarity", 0))
        lines.append(f"[Source: {c['source']} | Original: {c.get('original_source','N/A')} | Similarity: {sim}%]")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)


def build_sources(chunks):
    """Return sources with similarity percentages."""
    sources = []
    for c in chunks:
        sim = c.get("boosted_similarity", c.get("similarity", 0))
        sources.append({
            "source": c["source"],
            "similarity": sim
        })
    return sources

def answer_query(query: str, username: str = None, filename: str = None):
    print(f"[QUERY] {query} (User: {username}, File: {filename})")
    
    chunks = retriever.search(query, top_k=5, username=username)
    if filename:
        chunks = [c for c in chunks if os.path.basename(c.get("original_source", "")) == filename or c.get("source") == filename]
    
    if not chunks:
        return {"answer": "I couldn't find any relevant information in your uploaded documents.", "sources": []}

    context = format_context(chunks)
    sources = build_sources(chunks)
    
    lang = detect_language(query)
    
    prompt = f"""You are an intelligent document analysis assistant. 
Your goal is to answer the user's question accurately using ONLY the provided context from their uploaded documents.

Context from documents:
{context}

User question: "{query}"

Instructions:
1. Answer the question comprehensively based ONLY on the context above.
2. Do not hallucinate or use external knowledge.
3. If the context does not contain the answer, say exactly: "The information is not available in the provided documents."
4. Respond in the same language as the user's question (detected: {lang}).
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        answer = response.choices[0].message.content.strip()
        
        if "not available" in answer.lower() or "n'est pas disponible" in answer.lower() or "information is not available" in answer.lower():
            sources = []
            
        return {"answer": answer, "sources": sources}
    except Exception as e:
        print(f"LLM Error: {e}")
        # Fallback: if the LLM fails (e.g. out of quota), return the raw text chunks nicely formatted
        raw_text = "\n\n---\n\n".join([c["text"].strip() for c in chunks])
        return {"answer": raw_text or "L'information n'est pas disponible dans les documents.", "sources": sources}
