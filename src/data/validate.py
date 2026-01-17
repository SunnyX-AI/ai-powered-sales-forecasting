from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.data.checks import (
    CheckResult,
    require_columns,
    require_non_null,
    require_unique_key,
    require_range,
    require_allowed_values,
    join_coverage,
    no_column_collisions,
)


def _print_report(results: list[CheckResult]) -> None:
    failed = [r for r in results if not r.ok]

    for r in results:
        icon = "✅" if r.ok else "❌"
        line = f"{icon} {r.name}"
        if r.details:
            line += f" — {r.details}"
        print(line)

    if failed:
        raise ValueError(f"{len(failed)} data quality checks failed.")


# -----------------------------
# Suites (SunnyBest)
# -----------------------------
def validate_sales(df: pd.DataFrame) -> list[CheckResult]:
    results: list[CheckResult] = []

    results.append(require_columns(
        df,
        ["date", "store_id", "product_id", "units_sold", "price", "regular_price", "revenue"],
        "sales: required columns"
    ))
    results.append(require_non_null(df, ["date", "store_id", "product_id"], "sales: keys non-null"))
    results.append(require_unique_key(df, ["date", "store_id", "product_id"], "sales: unique grain"))

    results.append(require_range(df, "units_sold", 0, None, "sales: units_sold >= 0"))
    results.append(require_range(df, "price", 0, None, "sales: price >= 0"))
    results.append(require_range(df, "regular_price", 0, None, "sales: regular_price >= 0"))
    results.append(require_range(df, "discount_pct", 0, 100, "sales: discount_pct in [0,100]"))

    if "promo_flag" in df.columns:
        results.append(require_allowed_values(df, "promo_flag", [0, 1], "sales: promo_flag in {0,1}"))

    return results


def validate_merged(df: pd.DataFrame) -> list[CheckResult]:
    results: list[CheckResult] = []

    results.append(require_columns(
        df,
        ["date", "store_id", "product_id", "city", "category", "brand"],
        "merged: required columns"
    ))
    results.append(require_unique_key(df, ["date", "store_id", "product_id"], "merged: unique grain"))

    # Catch merge collisions
    results.append(no_column_collisions(df, ["_x", "_y"], "merged: no merge collision columns"))

    # Join coverage expectations (tune thresholds as you learn)
    results.append(join_coverage(df, ["product_name", "category", "brand"], 0.99, "merged: products join coverage"))
    results.append(join_coverage(df, ["store_name", "region", "city"], 0.99, "merged: stores join coverage"))
    results.append(join_coverage(df, ["temperature_c", "rainfall_mm"], 0.80, "merged: weather join coverage"))

    # Promo-event fields (if present)
    if "discount_pct_event" in df.columns:
        results.append(require_range(df, "discount_pct_event", 0, 100, "merged: discount_pct_event in [0,100]"))
    if "promo_flag_event" in df.columns:
        results.append(require_allowed_values(df, "promo_flag_event", [0, 1], "merged: promo_flag_event in {0,1}"))

    return results


# -----------------------------
# Runner
# -----------------------------
def run_validation(path: str) -> None:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    # Read CSV or Parquet
    if p.suffix == ".parquet":
        df = pd.read_parquet(p)
    else:
        df = pd.read_csv(p, parse_dates=["date"], low_memory=False)

    # Choose suite based on filename
    name = p.name.lower()
    if "merged" in name:
        results = validate_merged(df)
    elif "sales" in name:
        results = validate_sales(df)
    else:
        raise ValueError(
            f"Unknown dataset type for '{p.name}'. "
            "Expected filename to contain 'sales' or 'merged'."
        )

    _print_report(results)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m src.data.validate <path_to_dataset.csv|parquet>")

    run_validation(sys.argv[1])
