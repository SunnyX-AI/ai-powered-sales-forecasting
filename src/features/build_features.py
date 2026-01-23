"""
build_features.py

Feature engineering for SunnyBest models.

- Takes merged df from make_dataset.py
- Builds model-ready feature matrices
- Keeps logic consistent across notebooks, training, API, and dashboards
"""

from __future__ import annotations

from typing import Tuple, List, Optional
import pandas as pd
import numpy as np


# -----------------------------
# Feature selection helpers
# -----------------------------
def select_base_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select core explanatory features already validated in notebooks.
    No transformations yet — just clean selection.
    """

    feature_cols = [
        # pricing
        "price",
        "regular_price",
        "discount_pct",

        # promotion
        "promo_flag",

        # time
        "month",
        "is_weekend",
        "is_holiday",
        "is_payday",

        # product / store
        "category",
        "store_size",

        # weather
        "temperature_c",
        "rainfall_mm",
    ]

    existing = [c for c in feature_cols if c in df.columns]
    return df[existing].copy()


def encode_categoricals(X: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode categorical variables.
    Keeps numeric columns unchanged.
    """
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_cols:
        return X

    X_encoded = pd.get_dummies(
        X,
        columns=cat_cols,
        drop_first=True
    )
    return X_encoded


# -----------------------------
# Time-series feature helpers
# -----------------------------
def add_lag_rolling_features(
    df: pd.DataFrame,
    *,
    date_col: str = "date",
    target_col: str = "revenue",
    group_cols: Optional[List[str]] = None,
    lags: Optional[List[int]] = None,
    windows: Optional[List[int]] = None,
) -> pd.DataFrame:
    """
    Adds lag/rolling features for forecasting.
    Uses shift(1+) so it does NOT leak future values.
    """

    # Defensive checks
    if date_col not in df.columns:
        raise KeyError(f"Expected date column '{date_col}' not found in dataframe")

    if target_col not in df.columns:
        raise KeyError(f"Expected target column '{target_col}' not found in dataframe")

    if lags is None:
        lags = [1, 7, 14]
    if windows is None:
        windows = [7, 28]

    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")

    # If date parsing created NaTs, keep them but they'll likely be filtered later
    sort_cols = ([*group_cols, date_col] if group_cols else [date_col])
    out = out.sort_values(sort_cols)

    if group_cols:
        g = out.groupby(group_cols, sort=False)[target_col]

        # Lag features
        for lag in lags:
            out[f"{target_col}_lag_{lag}"] = g.shift(lag)

        # Rolling features computed on shifted series to prevent leakage
        shifted = g.shift(1)
        for w in windows:
            out[f"{target_col}_rollmean_{w}"] = (
                shifted.rolling(w).mean().reset_index(level=group_cols, drop=True)
            )
            out[f"{target_col}_rollstd_{w}"] = (
                shifted.rolling(w).std().reset_index(level=group_cols, drop=True)
            )
    else:
        # Lag features
        for lag in lags:
            out[f"{target_col}_lag_{lag}"] = out[target_col].shift(lag)

        # Rolling features on shifted series to prevent leakage
        shifted = out[target_col].shift(1)
        for w in windows:
            out[f"{target_col}_rollmean_{w}"] = shifted.rolling(w).mean()
            out[f"{target_col}_rollstd_{w}"] = shifted.rolling(w).std()

    return out


# -----------------------------
# Forecasting features
# -----------------------------
def build_forecast_features(
    df: pd.DataFrame,
    target: str = "revenue",
    date_col: str = "date",
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Build features and target for revenue forecasting.
    Adds lag/rolling features for time dependency.
    """

    if target not in df.columns:
        raise KeyError(f"Target column '{target}' not found in df")

    # If you have store_id/product_id in your merged df, use them here.
    # If you don't, the function will still work globally (less accurate).
    group_cols = [c for c in ["store_id", "product_id"] if c in df.columns]
    group_cols = group_cols if group_cols else None

    df_feat = add_lag_rolling_features(
        df,
        date_col=date_col,
        target_col=target,
        group_cols=group_cols,
    )

    # Base static features
    X = select_base_features(df_feat)

    # Add time-series engineered cols
    ts_cols = [
        c for c in df_feat.columns
        if c.startswith(f"{target}_lag_") or c.startswith(f"{target}_roll")
    ]
    if ts_cols:
        X = pd.concat([X, df_feat[ts_cols]], axis=1)

    X = encode_categoricals(X)
    y = df_feat[target]

    # Drop rows that don’t have enough history (lags/rolling -> NaNs)
    valid = X.notnull().all(axis=1) & y.notnull()
    X = X.loc[valid].copy()
    y = y.loc[valid].copy()

    return X, y


# -----------------------------
# Stockout classification features
# -----------------------------
def build_stockout_features(
    df: pd.DataFrame,
    target: str = "stockout_occurred",
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Build features and target for stockout classification.

    Note:
    - This is intentionally "static" for now (no lags),
      because stockout is strongly driven by inventory + promo/price context.
    - You can later add lagged demand/inventory signals if needed.
    """

    if target not in df.columns:
        raise KeyError(f"Target column '{target}' not found in df")

    feature_cols = [
        "price",
        "discount_pct",
        "promo_flag",
        "starting_inventory",
        "month",
        "is_weekend",
        "is_holiday",
        "category",
        "store_size",
    ]

    existing = [c for c in feature_cols if c in df.columns]
    if not existing:
        raise KeyError(
            "None of the expected stockout feature columns were found in df. "
            f"Expected one or more of: {feature_cols}"
        )

    X = df[existing].copy()
    X = encode_categoricals(X)

    # Make target robust to bool/int/0-1 values
    y = df[target]
    if y.dtype == bool:
        y = y.astype(int)
    else:
        y = pd.to_numeric(y, errors="coerce").fillna(0).astype(int)

    return X, y