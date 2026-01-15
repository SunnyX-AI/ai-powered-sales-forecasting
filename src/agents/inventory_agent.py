# src/agents/inventory_agent.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.models.predict import predict_from_row


@dataclass
class InventoryConstraints:
    # keep it simple v1
    target_service_level: float = 0.95          # not used deeply yet, placeholder for later
    max_stockout_probability: float = 0.40      # if predicted stockout > this, we trigger reorder
    safety_stock_units: int = 5                # minimum buffer
    max_reorder_units: int = 500               # prevent crazy recommendation


def recommend_reorder(
    payload: Dict[str, Any],
    constraints: InventoryConstraints = InventoryConstraints(),
) -> Dict[str, Any]:
    """
    Inventory Agent v1 (policy + model signal).

    payload must match /predict payload keys:
      price, regular_price, discount_pct, promo_flag, month, is_weekend, is_holiday, is_payday,
      category, store_size, temperature_c, rainfall_mm, starting_inventory
    """

    required = ["starting_inventory", "category", "store_size", "month"]
    for k in required:
        if k not in payload:
            return {"status": "error", "message": f"Missing required field: {k}"}

    # get model risk + revenue prediction
    pred = predict_from_row(payload)
    stock_prob = float(pred.get("stockout_probability", 0.0))
    predicted_revenue = float(pred.get("predicted_revenue", 0.0))

    current_inv = int(payload["starting_inventory"])

    # v1 logic: if stockout probability is high, reorder up to a buffer
    trigger = stock_prob >= constraints.max_stockout_probability

    if not trigger:
        return {
            "status": "ok",
            "trigger_reorder": False,
            "recommended_reorder_units": 0,
            "stockout_probability": stock_prob,
            "predicted_revenue": predicted_revenue,
            "why": [
                f"Stockout probability ({stock_prob:.3f}) is below threshold ({constraints.max_stockout_probability:.2f}).",
                "No reorder recommended under current policy.",
            ],
            "constraints": constraints.__dict__,
        }

    # simple reorder policy:
    # aim to raise inventory to (safety_stock + extra buffer)
    # extra buffer scales with risk band
    if stock_prob >= 0.7:
        buffer = 50
    elif stock_prob >= 0.5:
        buffer = 30
    else:
        buffer = 15

    target_inventory = constraints.safety_stock_units + buffer
    reorder_units = max(0, target_inventory - current_inv)
    reorder_units = min(reorder_units, constraints.max_reorder_units)

    return {
        "status": "ok",
        "trigger_reorder": True,
        "recommended_reorder_units": int(reorder_units),
        "target_inventory": int(target_inventory),
        "starting_inventory": int(current_inv),
        "stockout_probability": stock_prob,
        "predicted_revenue": predicted_revenue,
        "why": [
            f"Stockout probability ({stock_prob:.3f}) is above threshold ({constraints.max_stockout_probability:.2f}).",
            f"Recommended reorder raises inventory towards target buffer level ({target_inventory} units).",
        ],
        "constraints": constraints.__dict__,
    }