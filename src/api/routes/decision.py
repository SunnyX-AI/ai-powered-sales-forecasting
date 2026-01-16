# src/api/routes/decision.py
from __future__ import annotations

from typing import Any, Dict, Optional, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.agents.pricing_agent import PricingConstraints, recommend_price
from src.agents.inventory_agent import InventoryConstraints, recommend_reorder

router = APIRouter(prefix="/decision", tags=["decision"])


class DecisionPlanRequest(BaseModel):
    # payload must match /predict payload keys your models expect
    payload: Dict[str, Any]

    # pricing options
    pricing_objective: Literal["revenue", "profit"] = "revenue"
    max_discount_pct: float = 30.0
    max_stockout_probability_pricing: float = 0.60
    min_margin_pct: Optional[float] = None
    min_price_factor: float = 0.70
    max_price_factor: float = 1.30
    n_grid: int = 25

    # inventory options
    max_stockout_probability_inventory: float = 0.40
    safety_stock_units: int = 5
    max_reorder_units: int = 500


@router.post("/plan")
def decision_plan(req: DecisionPlanRequest) -> Dict[str, Any]:
    # --- run pricing agent ---
    pricing_constraints = PricingConstraints(
        max_discount_pct=req.max_discount_pct,
        max_stockout_probability=req.max_stockout_probability_pricing,
        min_margin_pct=req.min_margin_pct,
        min_price_factor=req.min_price_factor,
        max_price_factor=req.max_price_factor,
        n_grid=req.n_grid,
    )
    pricing_out = recommend_price(
        req.payload,
        constraints=pricing_constraints,
        objective=req.pricing_objective,
        return_table=True,
    )

    # --- run inventory agent ---
    inventory_constraints = InventoryConstraints(
        max_stockout_probability=req.max_stockout_probability_inventory,
        safety_stock_units=req.safety_stock_units,
        max_reorder_units=req.max_reorder_units,
    )
    inventory_out = recommend_reorder(req.payload, constraints=inventory_constraints)

    # --- combined plan (business-friendly) ---
    plan = {
        "pricing_action": pricing_out.get("recommendation") if pricing_out.get("status") == "ok" else None,
        "inventory_action": {
            "trigger_reorder": inventory_out.get("trigger_reorder"),
            "recommended_reorder_units": inventory_out.get("recommended_reorder_units"),
            "target_inventory": inventory_out.get("target_inventory"),
        } if inventory_out.get("status") == "ok" else None,
        "notes": [],
    }

    if pricing_out.get("status") != "ok":
        plan["notes"].append(f"Pricing agent did not return ok: {pricing_out.get('message', pricing_out.get('status'))}")
    if inventory_out.get("status") != "ok":
        plan["notes"].append(f"Inventory agent did not return ok: {inventory_out.get('message', inventory_out.get('status'))}")

    return {
        "status": "ok",
        "plan": plan,
        "pricing": pricing_out,
        "inventory": inventory_out,
    }