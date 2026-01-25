# src/forecasting/recursive_forecast.py
from __future__ import annotations

from typing import Optional, List
import pandas as pd
import numpy as np


def _canon_target_col(df: pd.DataFrame, target: str) -> str:
    """
    Your merged df sometimes has target columns with suffixes.
    Prefer exact target, else try target_x/target_y.
    """
    if target in df.columns:
        return target
    for cand in [f"{target}_y", f"{target}_x"]:
        if cand in df.columns:
            return cand
    raise KeyError(f"Target '{target}' not found. Available: {df.columns.tolist()}")


def recursive_forecast_revenue(
    *,
    history_df: pd.DataFrame,
    future_df: pd.DataFrame,
    model,
    build_features_fn,
    target: str = "revenue",
    date_col: str = "date",
    group_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Walk-forward forecasting:
    - predicts revenue for each future date
    - writes predictions back into future_df as 'pred_revenue'
    - also writes into a column named exactly target ('revenue') so lags can use it

    build_features_fn must be compatible with your build_forecast_features(df, target="revenue").
    """
    hist = history_df.copy()
    fut = future_df.copy()

    # Ensure datetime
    hist[date_col] = pd.to_datetime(hist[date_col], errors="coerce")
    fut[date_col] = pd.to_datetime(fut[date_col], errors="coerce")

    # Resolve target column name in history (handles revenue_x/revenue_y)
    hist_target_col = _canon_target_col(hist, target)

    # Standardize: make a clean target column name for feature builder
    if hist_target_col != target:
        hist[target] = hist[hist_target_col]
    # Future has no true target; we will fill it with predictions as we go.
    if target not in fut.columns:
        fut[target] = np.nan

    # Default grouping: store_id + product_id if present
    if group_cols is None:
        group_cols = [c for c in ["store_id", "product_id"] if c in fut.columns]
        group_cols = group_cols if group_cols else None

    # Sort future dates
    fut = fut.sort_values([date_col] + (group_cols if group_cols else [])).reset_index(drop=True)

    # We'll store outputs here
    fut["pred_revenue"] = np.nan

    # Iterate day-by-day
    unique_dates = sorted(fut[date_col].dropna().unique())

    for d in unique_dates:
        # Take all future rows up to and including date d
        fut_upto = fut[fut[date_col] <= d].copy()

        # Combine history + future (future has revenue filled only for dates already predicted)
        combined = pd.concat([hist, fut_upto], ignore_index=True, sort=False)

        # Build features for combined, then pick rows for date d
        X_all, y_all = build_features_fn(combined, target=target, date_col=date_col)

        # We need to align X/y back to combined's index after feature filtering.
        # build_forecast_features returns filtered rows, so we reconstruct a mask using y_all.index.
        valid_idx = y_all.index  # indices into combined after filtering

        combined_valid = combined.loc[valid_idx].copy()

        # Select only the rows for the current date d (these are the ones to predict now)
        mask_d = combined_valid[date_col] == d
        X_d = X_all.loc[mask_d]

        if len(X_d) == 0:
            continue

        preds = model.predict(X_d)

        # Write predictions into fut for date d
        # Need to match rows in fut for that date, but only those that survived filtering
        # We match by keys + date.
        keys = [date_col] + (group_cols if group_cols else [])
        pred_df = combined_valid.loc[mask_d, keys].copy()
        pred_df["pred_revenue"] = preds

        # Merge back into fut
        fut = fut.merge(pred_df, on=keys, how="left", suffixes=("", "_new"))
        fut["pred_revenue"] = fut["pred_revenue_new"].combine_first(fut["pred_revenue"])
        fut = fut.drop(columns=["pred_revenue_new"])

        # ALSO write into target column so future lags/rollings can use it
        fut[target] = fut["pred_revenue"].combine_first(fut[target])

    return fut