from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

import pandas as pd
from fastapi import FastAPI

from src.genai.schemas import AskRequest, AskResponse
from src.genai.router import route_question


app = FastAPI(
    title="AI-Powered Retail Decision Intelligence Platform",
    version="1.0.0",
    description="SunnyX Forecasting System API with pricing and GenAI support."
)


ELASTICITY_PATH = os.getenv("ELASTICITY_PATH", "data/processed/elasticity_by_category.csv")


def load_elasticity_table() -> pd.DataFrame:
    if os.path.exists(ELASTICITY_PATH):
        return pd.read_csv(ELASTICITY_PATH)
    return pd.DataFrame(columns=["category", "price_elasticity"])


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
    return {"status": "ok", "app": "main"}


@app.get("/pricing/elasticity", tags=["pricing"])
def get_elasticity(category: Optional[str] = None) -> Dict[str, Any]:
    df = load_elasticity_table()

    if df.empty:
        return {
            "items": [],
            "note": "Elasticity table not found. Build artifact first."
        }

    if category:
        df = df[df["category"] == category]

    return {"items": df.to_dict(orient="records")}


@app.post("/ask", response_model=AskResponse, tags=["genai"])
def ask(req: AskRequest) -> AskResponse:
    answer = route_question(
        question=req.question,
        payload=req.payload,
        docs=DOCS
    )
    return AskResponse(answer=answer)