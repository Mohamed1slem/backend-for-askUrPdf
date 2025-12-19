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

client = OpenAI()
retriever = Retriever()  # ✅ global retriever instance


def detect_language(text: str) -> str:
    text_lower = text.lower()
    if any(word in text_lower for word in ["hello", "hi", "what", "how", "service", "offer", "convention"]):
        return "en"
    if any(word in text_lower for word in ["واش", "كيفاش", "شحال", "علاش", "كاين"]):
        return "darija"
    return "fr"


def classify_intent(question: str) -> str:
    classification_prompt = f"""You are an intent classifier for an enterprise chatbot.

User question: "{question}"

Classify the intent into ONE of these categories:
GREETING, EXPLORATION, BUSINESS"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": "You are a classifier."},
                      {"role": "user", "content": classification_prompt}],
            temperature=0.1,
            max_tokens=10,
        )
        intent = response.choices[0].message.content.strip().upper()
        return intent if intent in ["GREETING", "EXPLORATION", "BUSINESS"] else "EXPLORATION"
    except Exception as e:
        print(f"Intent classification error: {e}")
        return "EXPLORATION"


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


def answer_query(query: str):
    facts = extract_memory_facts(query)
    if facts:
        write_memory(facts)
    mem = read_memory()

    lang = detect_language(query)
    intent = classify_intent(query)

    print(f"[QUERY] {query}")
    print(f"[INTENT] {intent} | [LANG] {lang}")

    # ---- GREETING ----
    if intent == "GREETING":
        if lang == "en":
            greeting = ("Hello. I am the Front Office assistant for Algérie Télécom.\n\n"
                        "I am here to help you understand our offers, particularly Idoom Fibre, "
                        "as well as our conventions, services, and procedures.\n\n"
                        "How can I help you today?")
        elif lang == "darija":
            greeting = ("السلام عليكم. أنا مساعد مكتب الاستقبال لاتصالات الجزائر.\n\n"
                        "أنا هنا لمساعدتك على فهم عروضنا، خاصة Idoom Fibre، "
                        "وكذلك اتفاقياتنا وخدماتنا وإجراءاتنا.\n\n"
                        "كيف يمكنني مساعدتك اليوم؟")
        else:
            greeting = ("Bonjour. Je suis l'assistant du Front Office d'Algérie Télécom.\n\n"
                        "Je suis là pour vous renseigner sur nos offres, en particulier Idoom Fibre, "
                        "ainsi que sur nos conventions, services et procédures.\n\n"
                        "Comment puis-je vous aider aujourd'hui ?")
        return {"answer": greeting, "sources": []}

    # ---- EXPLORATION ----
    if intent == "EXPLORATION":
        exploration_prompt = f"""You are a professional Front Office assistant for Algérie Télécom.

User question: "{query}"
Language: {lang}
User preferences (tone only): {mem}

Task:
- Provide a professional, helpful explanation
- Explain categories/services/offers
- Guide with clarifying questions
- DO NOT invent numbers or conditions
- Respond in {lang}."""

        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": exploration_prompt}],
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()
            return {"answer": answer, "sources": []}
        except Exception as e:
            print(f"Exploration LLM error: {e}")
            # ✅ Fallback: return top chunks directly
            chunks = retriever.search(query, top_k=3)
            context = "\n\n".join([c["text"] for c in chunks])
            sources = build_sources(chunks)
            return {"answer": context or FALLBACK_TEXT, "sources": sources}

    # ---- BUSINESS ----
    if intent == "BUSINESS":
        base = retriever.search(query, top_k=10)
        base = [c for c in base if c.get("boosted_similarity", c.get("similarity", 0)) >= MIN_SIMILARITY][:5]

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

        business_prompt = f"""Intent: BUSINESS
Language: {lang}
User preferences: {mem}

Question:
{query}

Context:
{context}

Instructions:
1. Use ONLY the context
2. NEVER use external knowledge
3. NEVER mix establishments
4. If context answers → respond precisely
5. If not → respond EXACTLY:
   "L'information n'est pas disponible dans les documents."
6. Respond in {lang}"""

        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": business_prompt}],
                temperature=0.1,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Business LLM error: {e}")
            # ✅ Fallback: return retrieved chunks directly
            context = format_context(base)
            sources = build_sources(base)
            return {"answer": context or FALLBACK_TEXT, "sources": sources}

        if answer == FALLBACK_TEXT or "n'est pas disponible" in answer or "not available" in answer:
            sources = []
        else:
            sources = build_sources(base) if base else []

        return {"answer": answer, "sources": sources}

    return {"answer": FALLBACK_TEXT, "sources": []}
