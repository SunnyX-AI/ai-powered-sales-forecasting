from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd


LOG_PATH = os.getenv("PREDICTIONS_LOG_PATH", "monitoring/predictions_log.csv")


def _ensure_parent_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def append_prediction_log(
    *,
    request_payload: Dict[str, Any],
    response_payload: Dict[str, Any],
    model_versions: Optional[Dict[str, str]] = None,
) -> None:
    """
    Appends one row per prediction to a CSV log for basic monitoring.
    """
    _ensure_parent_dir(LOG_PATH)

    row: Dict[str, Any] = {}

    # timestamp
    row["ts_utc"] = datetime.now(timezone.utc).isoformat()

    # model versions (optional)
    if model_versions:
        for k, v in model_versions.items():
            row[f"model_{k}_version"] = v

    # request fields (flattened)
    for k, v in request_payload.items():
        row[f"req_{k}"] = v

    # response fields (flattened)
    for k, v in response_payload.items():
        row[f"pred_{k}"] = v

    df_row = pd.DataFrame([row])

    if os.path.exists(LOG_PATH):
        df_row.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        df_row.to_csv(LOG_PATH, index=False)


def read_recent_predictions(limit: int = 50) -> pd.DataFrame:
    if not os.path.exists(LOG_PATH):
        return pd.DataFrame()

    df = pd.read_csv(LOG_PATH)
    # newest last → show newest first
    df = df.tail(limit).iloc[::-1].reset_index(drop=True)
    return df
