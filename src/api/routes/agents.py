# src/api/routes/agents.py
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.agents.pricing_agent import PricingConstraints, recommend_price


router = APIRouter(prefix="/agent", tags=["agents"])


class PricingAgentRequest(BaseModel):
    payload: Dict[str, Any]
    objective: str = Field("revenue", pattern="^(revenue|profit)$")

    # constraints (optional overrides)
    max_discount_pct: float = 30.0
    max_stockout_probability: float = 0.60
    min_margin_pct: Optional[float] = None
    min_price_factor: float = 0.70
    max_price_factor: float = 1.30
    n_grid: int = 25


@router.post("/pricing/recommend")
def pricing_recommend(req: PricingAgentRequest):
    c = PricingConstraints(
        max_discount_pct=req.max_discount_pct,
        max_stockout_probability=req.max_stockout_probability,
        min_margin_pct=req.min_margin_pct,
        min_price_factor=req.min_price_factor,
        max_price_factor=req.max_price_factor,
        n_grid=req.n_grid,
    )
    return recommend_price(req.payload, constraints=c, objective=req.objective, return_table=True)
