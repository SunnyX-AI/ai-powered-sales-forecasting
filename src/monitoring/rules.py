from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd


def generate_alerts(log_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Lightweight monitoring rules (simple, explainable).
    Returns a list of alert dicts.
    """
    alerts: List[Dict[str, Any]] = []

    if log_df is None or log_df.empty:
        alerts.append({
            "type": "info",
            "message": "No prediction logs found yet. Make a few /predict calls to populate monitoring.",
        })
        return alerts

    # Stockout-risk rule
    if "pred_stockout_probability" in log_df.columns:
        high_risk = log_df[log_df["pred_stockout_probability"] >= 0.7]
        if len(high_risk) > 0:
            alerts.append({
                "type": "risk",
                "message": f"{len(high_risk)} recent predictions have stockout_probability ≥ 0.7 (high risk).",
                "rule": "stockout_probability >= 0.7",
            })

    # Revenue anomaly rule (very simple distribution-based)
    if "pred_predicted_revenue" in log_df.columns:
        rev = pd.to_numeric(log_df["pred_predicted_revenue"], errors="coerce").dropna()
        if len(rev) >= 10:
            mu = float(np.mean(rev))
            sd = float(np.std(rev)) if float(np.std(rev)) > 0 else 1.0

            latest = float(rev.iloc[0])  # newest first
            if latest < mu - 2 * sd:
                alerts.append({
                    "type": "warning",
                    "message": "Latest predicted revenue looks unusually low vs recent history (below mean - 2σ).",
                    "rule": "latest_revenue < mean(recent) - 2*std(recent)",
                    "latest_predicted_revenue": latest,
                    "mean_recent": mu,
                    "std_recent": sd,
                })

    # Data-quality checks (missing key request fields)
    required_req_cols = ["req_category", "req_store_size", "req_month"]
    missing_cols = [c for c in required_req_cols if c not in log_df.columns]
    if missing_cols:
        alerts.append({
            "type": "warning",
            "message": f"Monitoring log is missing expected request columns: {missing_cols}.",
        })

    return alerts
