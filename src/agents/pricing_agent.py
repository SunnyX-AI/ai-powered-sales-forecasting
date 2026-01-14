# src/agents/pricing_agent.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import os

import numpy as np
import pandas as pd

from src.models.predict import predict_from_row


# -----------------------------
# Elasticity loading (artifact)
# -----------------------------
ELASTICITY_PATH = os.getenv("ELASTICITY_PATH", "data/processed/elasticity_by_category.csv")

def load_elasticity_table() -> pd.DataFrame:
    if os.path.exists(ELASTICITY_PATH):
        return pd.read_csv(ELASTICITY_PATH)
    return pd.DataFrame(columns=["category", "price_elasticity"])

ELASTICITY_TABLE = load_elasticity_table()


def get_elasticity_for_category(category: str) -> Optional[float]:
    if ELASTICITY_TABLE.empty:
        return None
    row = ELASTICITY_TABLE[ELASTICITY_TABLE["category"] == category]
    if row.empty:
        return None
    val = row.iloc[0].get("price_elasticity", None)
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return None
        return float(val)
    except Exception:
        return None


# -----------------------------
# Constraints + config
# -----------------------------
@dataclass
class PricingConstraints:
    max_discount_pct: float = 30.0
    max_stockout_probability: float = 0.60
    min_margin_pct: Optional[float] = None  # if you provide cost_price, enforce margin
    min_price_factor: float = 0.70          # -30%
    max_price_factor: float = 1.30          # +30%
    n_grid: int = 25                        # number of price points to test


def _compute_discount_pct(regular_price: float, price: float) -> float:
    if regular_price <= 0:
        return 0.0
    disc = (regular_price - price) / regular_price * 100.0
    return float(max(0.0, disc))


def _compute_margin_pct(price: float, cost_price: float) -> float:
    # margin% = (price - cost)/price
    if price <= 0:
        return -1e9
    return float((price - cost_price) / price * 100.0)


def recommend_price(
    payload: Dict[str, Any],
    constraints: PricingConstraints = PricingConstraints(),
    objective: str = "revenue",  # "revenue" or "profit"
    return_table: bool = True,
) -> Dict[str, Any]:
    """
    Pricing Agent v1 (optimisation, not rules).

    payload: must look like your /predict payload:
      price, regular_price, discount_pct, promo_flag, month, is_weekend, is_holiday, is_payday,
      category, store_size, temperature_c, rainfall_mm, starting_inventory

    Optional:
      cost_price (if you want profit optimisation + margin constraints)
    """
    # --- validate minimal fields ---
    required = ["price", "regular_price", "category"]
    for k in required:
        if k not in payload:
            return {"status": "error", "message": f"Missing required field: {k}"}

    base_price = float(payload["price"])
    regular_price = float(payload["regular_price"])
    category = str(payload["category"])

    cost_price = payload.get("cost_price", None)
    if cost_price is not None:
        try:
            cost_price = float(cost_price)
        except Exception:
            cost_price = None

    elasticity = get_elasticity_for_category(category)

    # --- candidate grid of prices ---
    lo = constraints.min_price_factor * base_price
    hi = constraints.max_price_factor * base_price
    if lo <= 0:
        lo = max(1.0, base_price * 0.5)

    candidate_prices = np.linspace(lo, hi, constraints.n_grid)

    evaluated: List[Dict[str, Any]] = []
    best: Optional[Dict[str, Any]] = None

    for p in candidate_prices:
        cand = dict(payload)
        cand["price"] = float(p)
        cand["discount_pct"] = _compute_discount_pct(regular_price, float(p))

        # hard constraint: max discount
        if cand["discount_pct"] > constraints.max_discount_pct:
            continue

        # score via your existing models
        try:
            pred = predict_from_row(cand)
            pred_rev = float(pred.get("predicted_revenue", 0.0))
            pred_stock = float(pred.get("stockout_probability", 0.0))
        except Exception:
            # if model fails for a candidate, skip it
            continue

        # hard constraint: stockout risk
        if pred_stock > constraints.max_stockout_probability:
            continue

        # optional margin constraint
        margin_pct = None
        if cost_price is not None:
            margin_pct = _compute_margin_pct(float(p), cost_price)
            if constraints.min_margin_pct is not None and margin_pct < constraints.min_margin_pct:
                continue

        # choose objective
        if objective == "profit" and cost_price is not None:
            # approximate profit using predicted revenue and margin%:
            # profit ≈ revenue * margin% (as a fraction)
            score = pred_rev * ((margin_pct or 0.0) / 100.0)
        else:
            score = pred_rev  # revenue objective

        row = {
            "candidate_price": float(p),
            "candidate_discount_pct": float(cand["discount_pct"]),
            "predicted_revenue": pred_rev,
            "stockout_probability": pred_stock,
            "elasticity": elasticity,
            "margin_pct": margin_pct,
            "objective": objective,
            "score": float(score),
        }
        evaluated.append(row)

        if best is None or row["score"] > best["score"]:
            best = row

    if not evaluated:
        return {
            "status": "no_solution",
            "message": "No price met the constraints. Try relaxing max_discount_pct or max_stockout_probability.",
            "elasticity": elasticity,
            "constraints": constraints.__dict__,
        }

    evaluated_df = pd.DataFrame(evaluated).sort_values("score", ascending=False).reset_index(drop=True)

    # explanation text (lightweight)
    why = []
    why.append(f"Tested {len(evaluated_df)} feasible price candidates within [{constraints.min_price_factor:.2f}x, {constraints.max_price_factor:.2f}x] of current price.")
    why.append(f"Applied constraints: discount≤{constraints.max_discount_pct:.0f}%, stockout≤{constraints.max_stockout_probability:.2f}.")
    if objective == "profit" and cost_price is not None:
        why.append("Optimised for profit (using cost_price).")
    else:
        why.append("Optimised for revenue (default).")
    if elasticity is not None:
        why.append(f"Elasticity reference for category '{category}': {elasticity:.3f} (informational).")

    result = {
        "status": "ok",
        "recommendation": {
            "current_price": base_price,
            "recommended_price": best["candidate_price"],
            "recommended_discount_pct": best["candidate_discount_pct"],
            "predicted_revenue": best["predicted_revenue"],
            "stockout_probability": best["stockout_probability"],
            "objective": best["objective"],
            "score": best["score"],
        },
        "why": why,
        "elasticity": elasticity,
        "constraints": constraints.__dict__,
    }

    if return_table:
        result["top_candidates"] = evaluated_df.head(10).to_dict(orient="records")

    return result
