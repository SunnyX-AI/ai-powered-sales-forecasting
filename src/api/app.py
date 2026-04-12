from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

from src.monitoring.store import read_recent_predictions
from src.monitoring.rules import generate_alerts
from src.planning.plan_q1 import run_revenue_plan
from src.genai.schemas import AskRequest, AskResponse
from src.genai.router import route_question


app = FastAPI(
    title="AI-Powered Retail Decision Intelligence Platform",
    version="1.0.0",
    description="SunnyX Forecasting System API with planning, monitoring, pricing, and GenAI support."
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


class RevenuePlanRequest(BaseModel):
    anchor_date: str = "2024-12-31"
    start_date: str = "2025-01-01"
    end_date: str = "2025-03-31"
    history_months: int = 6
    promo_flag: int = 0
    discount_pct: float = 0.0


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


@app.post("/plan/revenue", tags=["planning"])
def plan_revenue(req: RevenuePlanRequest) -> Dict[str, Any]:
    return run_revenue_plan(
        anchor_date=req.anchor_date,
        start_date=req.start_date,
        end_date=req.end_date,
        history_months=req.history_months,
        promo_flag=req.promo_flag,
        discount_pct=req.discount_pct,
    )


@app.post("/ask", response_model=AskResponse, tags=["genai"])
def ask(req: AskRequest) -> AskResponse:
    answer = route_question(
        question=req.question,
        payload=req.payload,
        docs=DOCS
    )
    return AskResponse(answer=answer)


@app.get("/monitoring/recent", tags=["monitoring"])
def monitoring_recent(limit: int = 50) -> Dict[str, Any]:
    df = read_recent_predictions(limit=limit)
    if df.empty:
        return {"items": [], "note": "No logs yet."}
    return {"items": df.to_dict(orient="records")}


@app.get("/monitoring/alerts", tags=["monitoring"])
def monitoring_alerts(limit: int = 200) -> Dict[str, Any]:
    df = read_recent_predictions(limit=limit)
    alerts = generate_alerts(df)
    return {"alerts": alerts, "count": len(alerts)}