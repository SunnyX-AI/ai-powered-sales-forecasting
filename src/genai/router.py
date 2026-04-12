from typing import Optional, Dict, Any, List
from src.genai.openai_client import get_chat_response


SYSTEM_PROMPT = """
You are the AI assistant for SunnyX Forecasting System (SFS).

Your job is to help explain the retail forecasting system in clear, professional language.

Rules:
- Be accurate and concise.
- If you are unsure, say so.
- Focus on retail forecasting, inventory, pricing, promotions, and stockout concepts.
- Do not invent database values, forecasts, or model outputs that were not provided.
"""


def build_docs_context(docs: List[dict]) -> str:
    if not docs:
        return ""

    chunks = []
    for doc in docs:
        title = doc.get("title", "Untitled")
        text = doc.get("text", "")
        chunks.append(f"Title: {title}\nContent: {text}")
    return "\n\n".join(chunks)


def search_docs(question: str, docs: List[dict]) -> Optional[str]:
    """
    Simple keyword-based doc search.
    Returns the first matching doc text if found.
    """
    q = question.lower()

    keyword_map = {
        "promotion": ["promo", "promotion", "promotions", "uplift", "discount"],
        "stockout": ["stockout", "inventory", "out of stock"],
        "pricing": ["price", "pricing", "elasticity"],
        "units_sold": ["units_sold", "units sold", "sales volume"],
        "revenue": ["revenue", "sales value"],
    }

    for doc in docs:
        title = doc.get("title", "").lower()
        text = doc.get("text", "").lower()
        combined = f"{title} {text}"

        for _, keywords in keyword_map.items():
            if any(k in q for k in keywords) and any(k in combined for k in keywords):
                return doc.get("text", "")

    return None


def offline_answer(
    question: str,
    payload: Optional[Dict[str, Any]] = None,
    docs: Optional[List[dict]] = None
) -> str:
    """
    Rule-based fallback so /ask works without OpenAI credits.
    """
    q = question.lower()
    payload = payload or {}
    docs = docs or []

    if "units_sold" in q or "units sold" in q:
        return "In SFS, units_sold represents the number of units of a product sold over a given period."

    if "stockout" in q:
        if "starting_inventory" in payload:
            inv = payload["starting_inventory"]
            return (
                f"A stockout occurs when available inventory cannot meet demand. "
                f"In this case, the provided starting_inventory is {inv}, which may increase stockout risk if demand is high."
            )
        return "A stockout occurs when available inventory cannot meet demand."

    if "promotion" in q or "promo" in q:
        return "Promotions typically increase demand, but they can also increase stockout risk if inventory is not sufficient."

    if "price" in q or "pricing" in q or "elasticity" in q:
        return "Pricing affects demand differently across categories. In SFS, pricing intelligence helps assess how price changes may influence sales and revenue."

    if "revenue" in q:
        return "Revenue in SFS is typically driven by units sold and price, and can be forecast to support planning decisions."

    doc_hit = search_docs(question, docs)
    if doc_hit:
        return doc_hit

    return "I’m currently running in offline mode. OpenAI billing is required for full GenAI responses, but I can still answer basic SFS questions."


def route_question(
    question: str,
    payload: Optional[Dict[str, Any]] = None,
    docs: Optional[List[dict]] = None
) -> str:
    payload = payload or {}
    docs = docs or []

    # 1. Try offline rules first for common SFS questions
    offline = offline_answer(question=question, payload=payload, docs=docs)

    # If offline gave a specific answer, return it directly
    # We only fall through to OpenAI when the fallback is generic
    if not offline.startswith("I’m currently running in offline mode"):
        return offline

    # 2. Try OpenAI for richer response
    docs_context = build_docs_context(docs)

    user_prompt = f"""
User Question:
{question}

Payload:
{payload}

Available Documentation:
{docs_context}
"""

    try:
        return get_chat_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
    except Exception:
        # 3. Final safe fallback
        return offline