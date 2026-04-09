from typing import Optional, Dict, Any, List
from src.genai.openai_client import get_chat_response


SYSTEM_PROMPT = """
You are the AI assistant for SunnyBest Forecasting System (SFS).

Your job is to help explain the retail forecasting system in clear, professional language.

Rules:
- Be accurate and concise.
- If you are unsure, say so.
- Focus on retail forecasting, inventory, pricing, promotions, and stockout concepts.
- Do not invent database values, forecasts, or model outputs that were not provided.
"""


def build_docs_context(docs: List[dict]) -> str:
    if not docs:
        return "No documents available."

    chunks = []
    for doc in docs:
        title = doc.get("title", "Untitled")
        text = doc.get("text", "")
        chunks.append(f"Title: {title}\nContent: {text}")
    return "\n\n".join(chunks)


def route_question(
    question: str,
    payload: Optional[Dict[str, Any]] = None,
    docs: Optional[List[dict]] = None
) -> str:
    payload = payload or {}
    docs = docs or []

    docs_context = build_docs_context(docs)

    user_prompt = f"""
User Question:
{question}

Payload:
{payload}

Available Documentation:
{docs_context}
"""

    return get_chat_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )