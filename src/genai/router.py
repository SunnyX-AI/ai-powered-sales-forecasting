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


def explain_stockout_from_payload(payload: Dict[str, Any]) -> str:
    starting_inventory = payload.get("starting_inventory")
    promo_flag = payload.get("promo_flag")
    discount_pct = payload.get("discount_pct")

    parts = []

    if starting_inventory is not None:
        if starting_inventory <= 5:
            parts.append(f"starting inventory is very low at {starting_inventory}")
        elif starting_inventory <= 20:
            parts.append(f"starting inventory is moderate at {starting_inventory}")
        else:
            parts.append(f"starting inventory is relatively healthy at {starting_inventory}")

    if promo_flag == 1:
        parts.append("a promotion is active, which may increase demand")

    if discount_pct is not None and discount_pct > 0:
        parts.append(f"the discount of {discount_pct}% may further increase sales pressure on inventory")

    if not parts:
        return "Stockout risk depends on how available inventory compares with demand."

    return "Stockout risk is influenced because " + "; ".join(parts) + "."


def explain_revenue_from_payload(payload: Dict[str, Any]) -> str:
    price = payload.get("price")
    units_sold = payload.get("units_sold")
    promo_flag = payload.get("promo_flag")
    discount_pct = payload.get("discount_pct")

    parts = []

    if price is not None:
        parts.append(f"price is {price}")

    if units_sold is not None:
        parts.append(f"units sold is {units_sold}")

    if promo_flag == 1:
        parts.append("promotion may be supporting sales volume")

    if discount_pct is not None and discount_pct > 0:
        parts.append(f"a {discount_pct}% discount may help increase units sold, though it can reduce margin")

    if not parts:
        return "Revenue is typically influenced by units sold and price."

    return "Revenue is being shaped by " + "; ".join(parts) + "."


def explain_pricing_from_payload(payload: Dict[str, Any]) -> str:
    price = payload.get("price")
    regular_price = payload.get("regular_price")
    discount_pct = payload.get("discount_pct")

    if price is None and regular_price is None and discount_pct is None:
        return "Pricing affects demand differently across categories and helps assess sales and revenue impact."

    parts = []

    if regular_price is not None:
        parts.append(f"regular price is {regular_price}")

    if price is not None:
        parts.append(f"current price is {price}")

    if discount_pct is not None:
        parts.append(f"discount percentage is {discount_pct}%")

    return "Pricing context shows that " + "; ".join(parts) + "."


def offline_answer(
    question: str,
    payload: Optional[Dict[str, Any]] = None,
    docs: Optional[List[dict]] = None
) -> str:
    q = question.lower()
    payload = payload or {}
    docs = docs or []

    if "units_sold" in q or "units sold" in q:
        if "units_sold" in payload:
            return f"In SFS, units_sold is the number of units sold. In this case, the provided units_sold value is {payload['units_sold']}."
        return "In SFS, units_sold represents the number of units of a product sold over a given period."

    if "stockout" in q:
        return explain_stockout_from_payload(payload)

    if "promotion" in q or "promo" in q:
        if payload.get("promo_flag") == 1:
            return "A promotion is active. Promotions typically increase demand, but they can also increase stockout risk if inventory is not sufficient."
        return "Promotions typically increase demand, but they can also increase stockout risk if inventory is not sufficient."

    if "price" in q or "pricing" in q or "elasticity" in q:
        return explain_pricing_from_payload(payload)

    if "revenue" in q:
        return explain_revenue_from_payload(payload)

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

    offline = offline_answer(question=question, payload=payload, docs=docs)

    if not offline.startswith("I’m currently running in offline mode"):
        return offline

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
        return offline