import os
import re
import requests
from dotenv import load_dotenv

from .config import SYSTEM_PROMPT, DEEPSEEK_API_URL, DEEPSEEK_MODEL
from .retriever import Retriever, expand_with_related

load_dotenv()

DEBUG_MODE = False
MIN_SIMILARITY = 60.0

# Lightweight, deterministic semantic groups
SEMANTIC_GROUPS = {
    "tarif": ["tarif", "tarifs", "préférentiel", "préférentiels", "preferentiel", "preferentiels", "avantageux"],
    "idoom_fibre": ["idoom fibre", "idoom", "internet", "services internet", "accès", "acces"],
    "couvre": ["inclut", "prévoit", "prevoyait", "prévoit", "prévoit", "bénéficie", "beneficie"],
}


def semantic_match(question: str, context: str) -> bool:
    """
    Returns True if the question uses any semantic group
    and the context contains at least one synonym from the same group.
    Deterministic, rule-based, no external knowledge.
    """
    q = (question or "").lower()
    ctx = (context or "").lower()

    for group, synonyms in SEMANTIC_GROUPS.items():
        # If the question mentions any word from this group
        if any(s in q for s in synonyms):
            # and the context contains any synonym from the same group
            if any(s in ctx for s in synonyms):
                return True
            # Question hits a group, but context doesn't: keep checking other groups
    return False
FALLBACK_TEXT = "L'information n'est pas disponible dans les documents."


def format_context(chunks):
    """
    Formats retrieved document chunks into a context string for the LLM.
    """
    lines = []
    for c in chunks:
        sim = c.get("boosted_similarity", c.get("similarity", 0))
        lines.append(
            f"[Source: {c['source']} | Original: {c.get('original_source','N/A')} | Similarity: {sim}%]"
        )
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)


def answer_query(query: str):
    """
    Final Front Office chatbot logic.
    - Non-business → LLM only, no sources
    - Business → RAG
    - Smart sources
    """
    print("Received query:", query)

    q = (query or "").lower()

    # -------------------------
    # BUSINESS INTENT DETECTION
    # -------------------------
    business_keywords = [
        "algérie télécom", "algerie telecom",
        "idoom", "fibre", "adsl", "vdsl",
        "offre", "offres",
        "convention",
        "procédure", "procedure",
        "service", "services",
        "établissement", "etablissement",
        "tarif", "tarifs",
    ]

    is_business = any(k in q for k in business_keywords)

    base = []
    context = ""
    est_id = None

    # =========================
    # BUSINESS MODE → RAG
    # =========================
    if is_business:
        retriever = Retriever()
        base = retriever.search(query, top_k=10)

        # similarity filter
        base = [
            c for c in base
            if c.get("boosted_similarity", c.get("similarity", 0)) >= MIN_SIMILARITY
        ]
        base = base[:5]

        # expand with related docs
        try:
            expanded_texts = expand_with_related(base, retriever.store, max_extra=4)
        except Exception:
            expanded_texts = [c["text"] for c in base]

        context_chunks = []
        base_texts = [c["text"] for c in base]

        for i, text in enumerate(expanded_texts):
            if i < len(base_texts):
                context_chunks.append(base[i])
            else:
                context_chunks.append({
                    "text": text,
                    "source": "related",
                    "original_source": "related",
                    "similarity": 100.0,
                    "boosted_similarity": 100.0,
                })

        context = format_context(context_chunks)

        # extract establishment id
        m = re.search(r"l[’']?établissement\s+([a-z])", query, re.IGNORECASE)
        if not m:
            m = re.search(r"etablissement\s+([a-z])", query, re.IGNORECASE)
        if m:
            est_id = m.group(1).upper()

        # Semantic answerability check: if no semantic match, fallback early
        if not semantic_match(query, context):
            # Smart sources logic unchanged below; compute and return early
            # Determine if the query is asking for detailed info
            detailed_keywords = [
                "tarif", "tarifs",
                "procédure", "procedure",
                "offre", "offres",
                "convention",
                "service", "services",
                "guide", "document", "page",
            ]
            wants_detail = any(k in q for k in detailed_keywords)

            if est_id and not wants_detail:
                sources = [f"L’établissement {est_id}"]
            else:
                sources = [
                    f"{c['source']} ({c.get('boosted_similarity', c.get('similarity', 0))}%)"
                    for c in base
                ]

            return {
                "answer": "L'information n'est pas disponible dans les documents.",
                "sources": sources,
            }

    # =========================
    # PROMPT
    # =========================
    if is_business:
        user_prompt = f"""
Question:
{query}

Context:
{context}
"""
    else:
        user_prompt = f"""
Question:
{query}
"""

    # =========================
    # API CALL
    # =========================
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {"answer": FALLBACK_TEXT, "sources": []}

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        answer = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
    except Exception as e:
        print("LLM error:", e)
        answer = FALLBACK_TEXT

    # =========================
    # SOURCES (SMART & FINAL)
    # =========================
    if answer == FALLBACK_TEXT:
        sources = []

    elif not is_business:
        sources = []

    else:
        detailed_keywords = [
            "tarif", "tarifs",
            "procédure", "procedure",
            "conditions", "détails", "details",
            "comment", "étapes", "etapes",
            "guide", "document", "page",
        ]
        wants_detail = any(k in q for k in detailed_keywords)

        if est_id and not wants_detail:
            sources = [f"L’établissement {est_id}"]
        else:
            sources = [
                f"{c['source']} ({c.get('boosted_similarity', c.get('similarity', 0))}%)"
                for c in base
            ]

    return {
        "answer": answer,
        "sources": sources
    }
