# src/forecasting/history_window.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence
import pandas as pd


@dataclass
class HistoryWindowConfig:
    months: int = 6
    date_col: str = "date"
    group_cols: Optional[Sequence[str]] = None  # e.g. ("store_id","product_id")
    require_min_history: bool = False          # if True, drop groups with too few days
    min_days: int = 60                         # used when require_min_history=True


def select_history_window(
    df: pd.DataFrame,
    *,
    months: int = 6,
    date_col: str = "date",
    anchor_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Select the last N months of history ending at anchor_date (or max date in df).

    - Used to create a clean 'base period' for forecasting (like AVW base window).
    - Returns a filtered copy of df.

    Params
    ------
    months: number of months to look back
    anchor_date: if provided, treat this as the 'as-at' date (e.g. December planning cut-off)

    Example
    -------
    hist = select_history_window(df, months=6, anchor_date="2024-12-31")
    """
    out = df.copy()

    if date_col not in out.columns:
        raise KeyError(f"Expected '{date_col}' column in df")

    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
    out = out[out[date_col].notna()].copy()

    if out.empty:
        raise ValueError("No valid dates found after parsing date column.")

    if anchor_date is None:
        end_date = out[date_col].max()
    else:
        end_date = pd.to_datetime(anchor_date)
        # keep only history up to anchor_date (important for proper backtesting)
        out = out[out[date_col] <= end_date].copy()

    start_date = (end_date - pd.DateOffset(months=months)).normalize()

    out = out[out[date_col] >= start_date].copy()
    return out


def select_history_window_by_config(df: pd.DataFrame, cfg: HistoryWindowConfig, anchor_date: Optional[str] = None) -> pd.DataFrame:
    """
    Convenience wrapper that supports optional group-level minimum-history filtering.
    """
    hist = select_history_window(df, months=cfg.months, date_col=cfg.date_col, anchor_date=anchor_date)

    if cfg.require_min_history and cfg.group_cols:
        # Drop groups with too few observations
        counts = hist.groupby(list(cfg.group_cols))[cfg.date_col].count()
        keep = counts[counts >= cfg.min_days].index
        hist = hist.set_index(list(cfg.group_cols))
        hist = hist.loc[hist.index.isin(keep)].reset_index()

    return hist