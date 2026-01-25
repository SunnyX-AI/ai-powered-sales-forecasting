# src/forecasting/future_frame.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal, List
import pandas as pd


@dataclass
class BaselineAssumptions:
    promo_flag: int = 0
    discount_pct: float = 0.0
    weather_strategy: Literal["monthly_city_mean", "global_mean"] = "monthly_city_mean"


def _pick_col(df: pd.DataFrame, candidates: List[str], *, name: str) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(
        f"Missing required field '{name}'. Tried columns: {candidates}. "
        f"Available columns: {df.columns.tolist()}"
    )


def make_future_dates(start_date: str, end_date: str) -> pd.DataFrame:
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    out = pd.DataFrame({"date": dates})
    out["month"] = out["date"].dt.month
    out["is_weekend"] = out["date"].dt.day_name().isin(["Saturday", "Sunday"])
    out["is_payday"] = out["date"].dt.day == 25

    fixed = {"01-01", "05-01", "10-01", "12-25", "12-26"}
    out["is_holiday"] = out["date"].dt.strftime("%m-%d").isin(fixed)
    return out


def build_future_frame(
    history_df: pd.DataFrame,
    start_date: str,
    end_date: str,
    assumptions: Optional[BaselineAssumptions] = None,
) -> pd.DataFrame:
    if assumptions is None:
        assumptions = BaselineAssumptions()

    df = history_df.copy()

    # Basic validation
    for col in ["date", "store_id", "product_id"]:
        if col not in df.columns:
            raise KeyError(f"history_df must contain '{col}'")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # IMPORTANT: include your merge suffix columns (_x/_y)
    city_col = _pick_col(df, ["city", "City", "store_city", "town", "location"], name="city")

    store_size_col = _pick_col(
        df,
        ["store_size", "store_size_y", "store_size_x", "Store_Size", "storeSize", "size"],
        name="store_size",
    )

    category_col = _pick_col(
        df,
        ["category", "category_y", "category_x", "Category", "product_category", "prod_category"],
        name="category",
    )

    reg_price_candidates = [
        "regular_price",
        "regular_price_y",
        "regular_price_x",
        "Regular_Price",
        "regularPrice",
        "list_price",
        "rrp",
    ]
    try:
        reg_price_col = _pick_col(df, reg_price_candidates, name="regular_price")
    except KeyError:
        if "price" in df.columns:
            reg_price_col = "price"
        else:
            raise

    # Canonical lookups
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

    # Ensure join keys are strings
    stores["store_id"] = stores["store_id"].astype(str)
    products["product_id"] = products["product_id"].astype(str)

    store_product = (
        stores.assign(_k=1)
        .merge(products.assign(_k=1), on="_k")
        .drop(columns="_k")
    )

    future_dates = make_future_dates(start_date, end_date)
    future = (
        future_dates.assign(_k=1)
        .merge(store_product.assign(_k=1), on="_k")
        .drop(columns="_k")
    )

    # Baseline promo + pricing
    future["promo_flag"] = int(assumptions.promo_flag)
    future["discount_pct"] = float(assumptions.discount_pct)
    future["price"] = future["regular_price"] * (1 - future["discount_pct"] / 100.0)

    # Weather baseline
    temp_col = "temperature_c" if "temperature_c" in df.columns else None
    rain_col = "rainfall_mm" if "rainfall_mm" in df.columns else None

    if assumptions.weather_strategy == "monthly_city_mean" and temp_col and rain_col:
        df["month_hist"] = df["date"].dt.month
        w = (
            df.groupby([city_col, "month_hist"], as_index=False)[[temp_col, rain_col]]
            .mean()
            .rename(columns={city_col: "city", "month_hist": "month", temp_col: "temperature_c", rain_col: "rainfall_mm"})
        )
        future = future.merge(w, on=["city", "month"], how="left")
        future["temperature_c"] = future["temperature_c"].fillna(df[temp_col].mean())
        future["rainfall_mm"] = future["rainfall_mm"].fillna(df[rain_col].mean())
    else:
        future["temperature_c"] = float(df[temp_col].mean()) if temp_col else 28.0
        future["rainfall_mm"] = float(df[rain_col].mean()) if rain_col else 2.0

    return future