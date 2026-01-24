# src/forecasting/future_frame.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal, List
from pathlib import Path
import pandas as pd
import numpy as np


# ==============================
# Assumptions (baseline)
# ==============================

@dataclass
class BaselineAssumptions:
    promo_flag: int = 0
    discount_pct: float = 0.0
    weather_strategy: Literal["monthly_city_mean", "global_mean"] = "monthly_city_mean"


# ==============================
# Small helpers
# ==============================

def _pick_col(df: pd.DataFrame, candidates: List[str], *, name: str) -> str:
    """Pick the first matching column name from candidates."""
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(
        f"Missing required field '{name}'. Tried columns: {candidates}. "
        f"Available columns: {df.columns.tolist()}"
    )


def make_future_dates(start_date: str, end_date: str) -> pd.DataFrame:
    """Build a calendar frame for future dates with simple flags."""
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    out = pd.DataFrame({"date": dates})

    out["month"] = out["date"].dt.month
    out["is_weekend"] = out["date"].dt.day_name().isin(["Saturday", "Sunday"])
    out["is_payday"] = out["date"].dt.day == 25

    # Simple fixed-holiday logic (same as your generator)
    fixed = {"01-01", "05-01", "10-01", "12-25", "12-26"}
    out["is_holiday"] = out["date"].dt.strftime("%m-%d").isin(fixed)

    return out


# ==============================
# Main: build future frame
# ==============================

def build_future_frame(
    history_df: pd.DataFrame,
    start_date: str,
    end_date: str,
    assumptions: Optional[BaselineAssumptions] = None,
) -> pd.DataFrame:
    """
    Create future rows for (date x store_id x product_id) with baseline assumptions.

    Requirements (flexible):
    - Must have store_id and product_id
    - Must have some city column (city/store_city/town/location)
    - Must have some store size column (store_size/Store_Size/storeSize/size)
    - Must have some product category column (category/product_category/Category)
    - Must have a regular/list price (regular_price/regularPrice/list_price/rrp/price)

    If regular_price is missing but price exists, we use price as a fallback.
    """
    if assumptions is None:
        assumptions = BaselineAssumptions()

    df = history_df.copy()

    # ---- Validate basics
    if "date" not in df.columns:
        raise KeyError("history_df must contain a 'date' column.")
    if "store_id" not in df.columns:
        raise KeyError("history_df must contain a 'store_id' column.")
    if "product_id" not in df.columns:
        raise KeyError("history_df must contain a 'product_id' column.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ---- Resolve column names (handles variants)
    city_col = _pick_col(df, ["city", "City", "store_city", "town", "location"], name="city")
    store_size_col = _pick_col(df, ["store_size", "Store_Size", "storeSize", "size"], name="store_size")
    category_col = _pick_col(df, ["category", "Category", "product_category", "prod_category"], name="category")

    # regular price can vary; fallback to 'price' if needed
    try:
        reg_price_col = _pick_col(
            df,
            ["regular_price", "Regular_Price", "regularPrice", "list_price", "rrp"],
            name="regular_price",
        )
    except KeyError:
        # fallback to 'price' if present (better than failing)
        if "price" in df.columns:
            reg_price_col = "price"
        else:
            raise

    # ---- Standardise minimal static tables into canonical names
    stores = (
        df[["store_id", city_col, store_size_col]]
        .drop_duplicates("store_id")
        .rename(columns={city_col: "city", store_size_col: "store_size"})
    )

    products = (
        df[["product_id", category_col, reg_price_col]]
        .drop_duplicates("product_id")
        .rename(columns={category_col: "category", reg_price_col: "regular_price"})
    )

    # Ensure ids are strings (safe joins + consistency)
    stores["store_id"] = stores["store_id"].astype(str)
    products["product_id"] = products["product_id"].astype(str)

    # ---- Cross join store x product grid
    store_product = (
        stores.assign(_k=1)
        .merge(products.assign(_k=1), on="_k")
        .drop(columns="_k")
    )

    # ---- Future dates + cross join
    future_dates = make_future_dates(start_date, end_date)
    future = (
        future_dates.assign(_k=1)
        .merge(store_product.assign(_k=1), on="_k")
        .drop(columns="_k")
    )

    # ---- Baseline promos + pricing
    future["promo_flag"] = int(assumptions.promo_flag)
    future["discount_pct"] = float(assumptions.discount_pct)
    future["price"] = future["regular_price"] * (1 - future["discount_pct"] / 100.0)

    # ---- Weather baseline (optional)
    # Try to locate weather cols; if missing, fill with sensible constants
    temp_col = "temperature_c" if "temperature_c" in df.columns else None
    rain_col = "rainfall_mm" if "rainfall_mm" in df.columns else None

    if assumptions.weather_strategy == "monthly_city_mean" and temp_col and rain_col:
        df["month"] = df["date"].dt.month
        w = (
            df.groupby([city_col, "month"], as_index=False)[[temp_col, rain_col]]
            .mean()
            .rename(columns={city_col: "city", temp_col: "temperature_c", rain_col: "rainfall_mm"})
        )

        future = future.merge(w, on=["city", "month"], how="left")

        # fallback if some (city,month) missing
        future["temperature_c"] = future["temperature_c"].fillna(df[temp_col].mean())
        future["rainfall_mm"] = future["rainfall_mm"].fillna(df[rain_col].mean())

    else:
        # global mean or no weather in history
        if temp_col:
            future["temperature_c"] = float(df[temp_col].mean())
        else:
            future["temperature_c"] = 28.0

        if rain_col:
            future["rainfall_mm"] = float(df[rain_col].mean())
        else:
            future["rainfall_mm"] = 2.0

    return future