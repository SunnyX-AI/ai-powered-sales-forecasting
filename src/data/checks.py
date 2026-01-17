from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Optional

import pandas as pd


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str = ""


def require_columns(df: pd.DataFrame, cols: Sequence[str], name: str) -> CheckResult:
    missing = [c for c in cols if c not in df.columns]
    ok = len(missing) == 0
    details = "" if ok else f"Missing columns: {missing}"
    return CheckResult(name, ok, details)


def require_non_null(df: pd.DataFrame, cols: Sequence[str], name: str) -> CheckResult:
    null_counts = df[list(cols)].isna().sum()
    bad = null_counts[null_counts > 0]
    ok = bad.empty
    details = "" if ok else f"Null counts: {bad.to_dict()}"
    return CheckResult(name, ok, details)


def require_unique_key(df: pd.DataFrame, key_cols: Sequence[str], name: str) -> CheckResult:
    dupes = int(df.duplicated(subset=list(key_cols)).sum())
    ok = dupes == 0
    details = "" if ok else f"Duplicate rows on {list(key_cols)}: {dupes}"
    return CheckResult(name, ok, details)


def require_range(
    df: pd.DataFrame,
    col: str,
    low: Optional[float],
    high: Optional[float],
    name: str,
) -> CheckResult:
    if col not in df.columns:
        return CheckResult(name, False, f"Column '{col}' not found")

    s = df[col]
    bad = pd.Series(False, index=df.index)

    if low is not None:
        bad |= s < low
    if high is not None:
        bad |= s > high

    n_bad = int(bad.sum())
    ok = n_bad == 0
    details = "" if ok else f"{col} out of range: {n_bad} rows"
    return CheckResult(name, ok, details)


def require_allowed_values(df: pd.DataFrame, col: str, allowed: Iterable, name: str) -> CheckResult:
    if col not in df.columns:
        return CheckResult(name, False, f"Column '{col}' not found")

    allowed = list(allowed)
    bad = ~df[col].isin(allowed) & df[col].notna()
    n_bad = int(bad.sum())
    ok = n_bad == 0
    details = "" if ok else f"{col} has {n_bad} invalid values. Allowed={allowed}"
    return CheckResult(name, ok, details)


def join_coverage(df: pd.DataFrame, cols: Sequence[str], threshold: float, name: str) -> CheckResult:
    """
    % of rows where ALL specified columns are non-null.
    Useful to detect silent merge failures.
    """
    missing_cols = [c for c in cols if c not in df.columns]
    if missing_cols:
        return CheckResult(name, False, f"Missing columns for coverage: {missing_cols}")

    coverage = float(df[list(cols)].notna().all(axis=1).mean())
    ok = coverage >= threshold
    details = f"Coverage={coverage:.3f} (threshold={threshold:.3f})"
    return CheckResult(name, ok, details)


def no_column_collisions(df: pd.DataFrame, forbidden_substrings: Sequence[str], name: str) -> CheckResult:
    """
    Catch columns like city_x, city_y, *_x, *_y that indicate merge collisions.
    """
    cols = df.columns.astype(str)
    bad = [c for c in cols if any(sub in c for sub in forbidden_substrings)]
    ok = len(bad) == 0
    details = "" if ok else f"Found collision-like columns: {bad}"
    return CheckResult(name, ok, details)
