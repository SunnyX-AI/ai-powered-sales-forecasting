"""
FastAPI app for SunnyBest Retail Demand Intelligence System.

Endpoints:
- GET  /health
- POST /predict  -> revenue forecast + stockout probability + risk band
- GET  /predict/example -> run prediction using a real row from merged df
- GET  /pricing/elasticity -> elasticity table
- GET  /monitoring/recent -> recent prediction logs
- GET  /monitoring/alerts -> simple alert rules
- POST /ask -> GenAI copilot
- POST /plan/revenue -> Q1 (or any range) revenue planning output (AVW-style monthly totals)
"""

from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.models.predict import predict_from_row, predict_example_from_existing_data
from src.monitoring.store import append_prediction_log, read_recent_predictions
from src.monitoring.rules import generate_alerts
from src.api.routes.agents import router as agents_router
from src.api.routes.decision import router as decision_router
from src.api.routes.predict import router as predict_router
from src.planning.plan_q1 import run_revenue_plan

# ✅ NEW GENAI IMPORTS
from src.genai.schemas import AskRequest, AskResponse
from src.genai.router import route_question


app = FastAPI(
    title="AI-Powered Retail Decision Intelligence Platform",
    version="1.0.0",
    description="Forecast revenue and predict stockout risk. Built from the SunnyBest project pipeline."
)

app.include_router(agents_router)
app.include_router(decision_router)
app.include_router(predict_router)


# -----------------------------
# Load artifacts at startup
# -----------------------------

ELASTICITY_PATH = os.getenv("ELASTICITY_PATH", "data/processed/elasticity_by_category.csv")


def load_elasticity_table() -> pd.DataFrame:
    if os.path.exists(ELASTICITY_PATH):
        return pd.read_csv(ELASTICITY_PATH)
    return pd.DataFrame(columns=["category", "price_elasticity"])


ELASTICITY_TABLE = load_elasticity_table()


# Minimal docs store (later replace with file-based docs / RAG)
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
]


# -----------------------------
# Request / Response Schemas
# -----------------------------
class PredictRequest(BaseModel):
    # Pricing
    price: float = Field(..., ge=0)
    regular_price: float = Field(..., ge=0)
    discount_pct: float = Field(0, ge=0, le=100)
    promo_flag: int = Field(0, ge=0, le=1)

    # Time
    month: int = Field(..., ge=1, le=12)
    is_weekend: int = Field(0, ge=0, le=1)
    is_holiday: int = Field(0, ge=0, le=1)
    is_payday: int = Field(0, ge=0, le=1)

    # Product / Store
    category: str
    store_size: str

    # Weather
    temperature_c: float
    rainfall_mm: float

    # Inventory
    starting_inventory: int = Field(..., ge=0)


class PredictResponse(BaseModel):
    predicted_revenue: float
    stockout_probability: float
    stockout_risk_band: str


class RevenuePlanRequest(BaseModel):
    anchor_date: str = "2024-12-31"
    start_date: str = "2025-01-01"
    end_date: str = "2025-03-31"
    history_months: int = 6
    promo_flag: int = 0
    discount_pct: float = 0.0


# -----------------------------
# Routes
# -----------------------------
@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.get("/pricing/elasticity", tags=["pricing"])
def get_elasticity(category: Optional[str] = None) -> Dict[str, Any]:
    """
    GET /pricing/elasticity
    GET /pricing/elasticity?category=Mobile%20Phones
    """
    df = load_elasticity_table()

    if df.empty:
        return {
            "items": [],
            "note": "Elasticity table not found. Build artifact first."
        }

    if category:
        df = df[df["category"] == category]

    return {"items": df.to_dict(orient="records")}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    payload = req.model_dump()
    out = predict_from_row(payload)

    p = float(out.get("stockout_probability", 0.0))
    if p >= 0.7:
        band = "HIGH"
    elif p >= 0.4:
        band = "MEDIUM"
    else:
        band = "LOW"

    out["stockout_risk_band"] = band

    try:
        append_prediction_log(request_payload=payload, response_payload=out)
    except Exception:
        pass

    return PredictResponse(**out)


@app.get("/predict/example")
def predict_example(
    date: Optional[str] = None,
    store_id: Optional[int] = None,
    product_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Example usage:
    /predict/example
    /predict/example?store_id=1
    /predict/example?product_id=1001
    /predict/example?date=2024-12-25&store_id=1&product_id=1001
    """
    return predict_example_from_existing_data(date=date, store_id=store_id, product_id=product_id)


@app.post("/plan/revenue", tags=["planning"])
def plan_revenue(req: RevenuePlanRequest) -> Dict[str, Any]:
    """
    Planning endpoint:
    - Uses last N months before anchor_date as history
    - Builds future frame for [start_date, end_date]
    - Runs recursive forecast
    - Returns monthly totals (AVW-style)
    """
    return run_revenue_plan(
        anchor_date=req.anchor_date,
        start_date=req.start_date,
        end_date=req.end_date,
        history_months=req.history_months,
        promo_flag=req.promo_flag,
        discount_pct=req.discount_pct,
    )


# ✅ UPDATED /ask ENDPOINT
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
        return {"items": [], "note": "No logs yet. Make some /predict calls first."}
    return {"items": df.to_dict(orient="records")}


@app.get("/monitoring/alerts", tags=["monitoring"])
def monitoring_alerts(limit: int = 200) -> Dict[str, Any]:
    df = read_recent_predictions(limit=limit)
    alerts = generate_alerts(df)
    return {"alerts": alerts, "count": len(alerts)}