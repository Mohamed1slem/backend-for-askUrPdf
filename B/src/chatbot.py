import os
import re
import requests
from dotenv import load_dotenv

from .config import SYSTEM_PROMPT, DEEPSEEK_API_URL, DEEPSEEK_MODEL
from .memory import read_memory, write_memory, extract_memory_facts
from .retriever import Retriever, expand_with_related

load_dotenv()

MIN_SIMILARITY = 60.0
FALLBACK_TEXT = "L'information n'est pas disponible dans les documents."


def detect_language(text: str) -> str:
    """Detect user's language: French, English, or Algerian Darija."""
    text_lower = text.lower()
    
    # English markers
    if any(word in text_lower for word in ["hello", "hi", "what", "how", "service", "offer", "convention"]):
        return "en"
    
    # Darija markers
    if any(word in text_lower for word in ["واش", "كيفاش", "شحال", "علاش", "كاين"]):
        return "darija"
    
    # Default to French (primary language)
    return "fr"


def classify_intent(question: str, api_key: str) -> str:
    """
    Use LLM to classify user intent into: GREETING, EXPLORATION, or BUSINESS.
    This replaces keyword-based detection for better accuracy.
    """
    classification_prompt = f"""You are an intent classifier for an enterprise chatbot.

User question: "{question}"

Classify the intent into ONE of these categories:

1. GREETING - polite exchanges, greetings, asking who you are
   Examples: "bonjour", "hello", "who are you?", "what can you do?"

2. EXPLORATION - general orientation, asking what exists, understanding services
   Examples: "tell me about fibre offers", "what services do you provide?", 
   "what are conventions?", "explain enterprise offers"

3. BUSINESS - specific factual question requiring precise document lookup
   Examples: "tarifs for establishment X", "procedure to subscribe", 
   "advantages of convention with Y", "required documents"

Respond with ONLY ONE WORD: GREETING or EXPLORATION or BUSINESS"""

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": classification_prompt}],
                "temperature": 0.1,
                "max_tokens": 10,
            },
            timeout=10,
        )
        response.raise_for_status()
        intent = response.json()["choices"][0]["message"]["content"].strip().upper()
        
        # Validate response
        if intent in ["GREETING", "EXPLORATION", "BUSINESS"]:
            return intent
        else:
            # Default to EXPLORATION if unclear (safer than BUSINESS)
            return "EXPLORATION"
            
    except Exception as e:
        print(f"Intent classification error: {e}")
        # Default to EXPLORATION (better UX than forcing BUSINESS fallback)
        return "EXPLORATION"


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
    Enterprise-grade Front Office chatbot with intent-driven architecture.
    
    Three behaviors:
    1. GREETING → Polite response, no RAG, no sources
    2. EXPLORATION → Professional guidance, no RAG, no sources
    3. BUSINESS → RAG with strict document grounding, sources only when answer found
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {"answer": FALLBACK_TEXT, "sources": []}
    
    # Extract user preferences (tone only)
    facts = extract_memory_facts(query)
    if facts:
        write_memory(facts)
    mem = read_memory()
    
    # Detect language and intent
    lang = detect_language(query)
    intent = classify_intent(query, api_key)
    
    print(f"[QUERY] {query}")
    print(f"[INTENT] {intent} | [LANG] {lang}")
    
    # ═══════════════════════════════════════════
    # GREETING INTENT → No RAG
    # ═══════════════════════════════════════════
    if intent == "GREETING":
        if lang == "en":
            greeting = "Hello. I am the Front Office assistant for Algérie Télécom.\n\n"
            greeting += "I am here to help you understand our offers, particularly Idoom Fibre, "
            greeting += "as well as our conventions, services, and procedures.\n\n"
            greeting += "How can I help you today?"
        elif lang == "darija":
            greeting = "السلام عليكم. أنا مساعد مكتب الاستقبال لاتصالات الجزائر.\n\n"
            greeting += "أنا هنا لمساعدتك على فهم عروضنا، خاصة Idoom Fibre، "
            greeting += "وكذلك اتفاقياتنا وخدماتنا وإجراءاتنا.\n\n"
            greeting += "كيف يمكنني مساعدتك اليوم؟"
        else:  # French
            greeting = "Bonjour. Je suis l'assistant du Front Office d'Algérie Télécom.\n\n"
            greeting += "Je suis là pour vous renseigner sur nos offres, en particulier Idoom Fibre, "
            greeting += "ainsi que sur nos conventions, services et procédures.\n\n"
            greeting += "Comment puis-je vous aider aujourd'hui ?"
        
        return {"answer": greeting, "sources": []}
    
    # ═══════════════════════════════════════════
    # EXPLORATION INTENT → Professional guidance WITHOUT RAG
    # ═══════════════════════════════════════════
    if intent == "EXPLORATION":
        exploration_prompt = f"""You are a professional Front Office assistant for Algérie Télécom.

The user is asking an EXPLORATION question (not looking for specific facts, just understanding what exists).

User question: "{query}"
Language: {lang}
User preferences (tone only): {mem}

Your task:
- Provide a professional, helpful explanation
- Explain what categories/services/offers exist
- Guide the user with clarifying questions
- DO NOT say "information not available"
- DO NOT invent specific numbers, prices, or conditions
- Be warm and helpful

Respond in {lang}."""

        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [{"role": "user", "content": exploration_prompt}],
                    "temperature": 0.7,
                },
                timeout=20,
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"].strip()
            return {"answer": answer, "sources": []}
        except Exception as e:
            print(f"Exploration LLM error: {e}")
            return {"answer": FALLBACK_TEXT, "sources": []}
    
    # ═══════════════════════════════════════════
    # BUSINESS INTENT → RAG
    # ═══════════════════════════════════════════
    if intent == "BUSINESS":
        # Retrieve documents
        retriever = Retriever()
        base = retriever.search(query, top_k=10)

        # Filter by similarity threshold
        base = [
            c for c in base
            if c.get("boosted_similarity", c.get("similarity", 0)) >= MIN_SIMILARITY
        ]
        base = base[:5]

        # Expand with related documents
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

        # Extract establishment ID for source filtering
        est_id = None
        m = re.search(r"l['']?établissement\s+([a-z])", query, re.IGNORECASE)
        if not m:
            m = re.search(r"etablissement\s+([a-z])", query, re.IGNORECASE)
        if m:
            est_id = m.group(1).upper()

        # Build business prompt with strict instructions
        business_prompt = f"""Intent: BUSINESS (question concrète)
Language: {lang}
User preferences (tone only): {mem}

Question:
{query}

Context documentaire:
{context}

Instructions STRICTES:
1. Utilise UNIQUEMENT le contexte fourni
2. NE JAMAIS utiliser de connaissances externes
3. NE JAMAIS mélanger les établissements
4. Si le contexte répond clairement → réponds avec précision
5. Si le contexte NE contient PAS la réponse → réponds EXACTEMENT:
   "L'information n'est pas disponible dans les documents."
6. Réponds en {lang}"""

        # Call LLM for business answer
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [{"role": "user", "content": business_prompt}],
                    "temperature": 0.1,
                },
                timeout=20,
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Business LLM error: {e}")
            answer = FALLBACK_TEXT

        # STRICT ENTERPRISE RULE: If fallback, sources MUST be empty
        if answer == FALLBACK_TEXT or "n'est pas disponible" in answer or "not available" in answer:
            sources = []
        elif est_id:
            sources = [f"L'établissement {est_id}"]
        else:
            sources = [
                f"{c['source']}"
                for c in base
            ] if base else []

        return {"answer": answer, "sources": sources}
    
    # Fallback (should never reach here)
    return {"answer": FALLBACK_TEXT, "sources": []}
