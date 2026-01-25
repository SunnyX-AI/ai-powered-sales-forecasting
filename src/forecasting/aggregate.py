# src/forecasting/aggregate.py
from __future__ import annotations

import pandas as pd


def aggregate_daily(forecast_df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Daily totals across all stores/products.
    Expects 'pred_revenue' in forecast_df.
    """
    df = forecast_df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    out = (
        df.groupby(date_col, as_index=False)["pred_revenue"]
        .sum()
        .rename(columns={"pred_revenue": "pred_revenue_total"})
        .sort_values(date_col)
    )
    return out


def aggregate_monthly(
    forecast_df: pd.DataFrame,
    date_col: str = "date",
    by: list[str] | None = None,
) -> pd.DataFrame:
    """
    Monthly totals, optionally grouped by columns (e.g., store_id, category).
    """
    df = forecast_df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month

    group_cols = ["year", "month"]
    if by:
        group_cols += by

    out = (
        df.groupby(group_cols, as_index=False)["pred_revenue"]
        .sum()
        .rename(columns={"pred_revenue": "pred_revenue_total"})
        .sort_values(group_cols)
    )
    return out


def aggregate_quarter(
    forecast_df: pd.DataFrame,
    date_col: str = "date",
    by: list[str] | None = None,
) -> pd.DataFrame:
    """
    Quarter totals (e.g., Q1, Q2), optionally grouped.
    """
    df = forecast_df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["year"] = df[date_col].dt.year
    df["quarter"] = df[date_col].dt.quarter

    group_cols = ["year", "quarter"]
    if by:
        group_cols += by

    out = (
        df.groupby(group_cols, as_index=False)["pred_revenue"]
        .sum()
        .rename(columns={"pred_revenue": "pred_revenue_total"})
        .sort_values(group_cols)
    )
    return out