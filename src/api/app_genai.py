"""
Minimal FastAPI app for testing GenAI in SunnyBest.

Endpoints:
- GET  /health
- POST /ask
"""

from __future__ import annotations

from typing import Dict, Any, List

from fastapi import FastAPI

from src.genai.schemas import AskRequest, AskResponse
from src.genai.router import route_question


app = FastAPI(
    title="SunnyBest GenAI Test API",
    version="1.0.0",
    description="Minimal GenAI-only app for testing the /ask endpoint."
)


# Minimal docs store for testing
DOCS: List[dict] = [
    {
        "title": "Promo uplift summary",
        "text": "Promotions show uplift strongest in Mobile Phones and Accessories."
    },
    {
        "title": "Stockout model summary",
        "text": "Stockouts increase with high demand, promotions, and low starting inventory."
    },
    {
        "title": "Pricing optimisation summary",
        "text": "Pricing simulation suggests revenue responds to price changes differently by category."
    },
    {
        "title": "Units sold definition",
        "text": "units_sold represents the number of units of a product sold at a given store over a given period."
    }
]


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "app": "genai_test"}


@app.post("/ask", response_model=AskResponse, tags=["genai"])
def ask(req: AskRequest) -> AskResponse:
    answer = route_question(
        question=req.question,
        payload=req.payload,
        docs=DOCS
    )
    return AskResponse(answer=answer)