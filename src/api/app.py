"""
FastAPI app for SunnyBest Retail Demand Intelligence System.

Endpoints:
- GET  /health
- POST /predict  -> revenue forecast + stockout probability + risk band
- GET  /predict/example -> run prediction using a real row from merged df
- GET  /pricing/elasticity -> elasticity table
- GET  /monitoring/recent -> recent prediction logs
- GET  /monitoring/alerts -> simple alert rules
- POST /ask -> GenAI copilot (experimental)
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
from src.genai.copilot import run_copilot
from src.api.routes.agents import router as agents_router


app = FastAPI(
    title="AI-Powered Retail Decision Intelligence Platform",
    version="1.0.0",
    description="Forecast revenue and predict stockout risk. Built from the SunnyBest project pipeline."
)
app.include_router(agents_router)
# -----------------------------
# Load artifacts at startup
# -----------------------------

# Elasticity table (pricing intelligence)
ELASTICITY_PATH = os.getenv("ELASTICITY_PATH", "data/processed/elasticity_by_category.csv")


def load_elasticity_table() -> pd.DataFrame:
    if os.path.exists(ELASTICITY_PATH):
        return pd.read_csv(ELASTICITY_PATH)
    return pd.DataFrame(columns=["category", "price_elasticity"])


ELASTICITY_TABLE = load_elasticity_table()


# Minimal docs store (later you can load from files)
DOCS: List[dict] = [
    {"title": "Promo uplift summary", "text": "Promotions show uplift strongest in Mobile Phones and Accessories..."},
    {"title": "Stockout model summary", "text": "Stockouts increase with high demand, promotions, and low starting inventory..."},
    {"title": "Pricing optimisation summary", "text": "Pricing simulation suggests revenue responds to price changes differently by category..."},
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

    # Inventory (needed for stockout model)
    starting_inventory: int = Field(..., ge=0)


class PredictResponse(BaseModel):
    predicted_revenue: float
    stockout_probability: float
    stockout_risk_band: str


class AskRequest(BaseModel):
    query: str
    payload: Optional[Dict[str, Any]] = None


# -----------------------------
# Routes
# -----------------------------
@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


# Pricing Intelligence
@app.get("/pricing/elasticity", tags=["pricing"])
def get_elasticity(category: Optional[str] = None):
    """
    GET /pricing/elasticity
    GET /pricing/elasticity?category=Mobile%20Phones
    """
    df = load_elasticity_table()  # reload each call

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

    # Risk band (interpretable)
    p = float(out.get("stockout_probability", 0.0))
    if p >= 0.7:
        band = "HIGH"
    elif p >= 0.4:
        band = "MEDIUM"
    else:
        band = "LOW"

    out["stockout_risk_band"] = band

    # Log for monitoring (do not break serving if logging fails)
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


@app.post("/ask", tags=["genai"])
def ask(req: AskRequest):
    payload = req.payload or {}
    return run_copilot(req.query, payload, DOCS)


@app.get("/monitoring/recent",tags=["monitoring"])
def monitoring_recent(limit: int = 50) -> Dict[str, Any]:
    df = read_recent_predictions(limit=limit)
    if df.empty:
        return {"items": [], "note": "No logs yet. Make some /predict calls first."}
    return {"items": df.to_dict(orient="records")}


@app.get("/monitoring/alerts")
def monitoring_alerts(limit: int = 200) -> Dict[str, Any]:
    df = read_recent_predictions(limit=limit)
    alerts = generate_alerts(df)
    return {"alerts": alerts, "count": len(alerts)}
