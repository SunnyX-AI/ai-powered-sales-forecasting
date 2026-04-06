# generate_weekly_forecast.py

import os
import warnings

import joblib
import pandas as pd

warnings.filterwarnings("ignore")


# -----------------------------
# Config
# -----------------------------
DATA_PATH = "data/processed/weekly_sales_v4_promotions.csv"
FORECAST_PATH = "data/outputs/weekly_forecasts.csv"

# Choose your current best model here
BEST_MODEL_PATH = "models/weekly_model_v4_promotions.pkl"
MODEL_VERSION = "weekly_model_v4_promotions"

TARGET = "units_sold"


# -----------------------------
# Load data
# -----------------------------
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_model(path: str):
    return joblib.load(path)


# -----------------------------
# Prepare data
# -----------------------------
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["week_start"] = pd.to_datetime(df["week_start"], errors="coerce")
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")

    df["store_id"] = df["store_id"].astype(str)
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce").astype("Int64")

    df = df.dropna(subset=["week_start", "store_id", "product_id", TARGET])
    df["product_id"] = df["product_id"].astype(int)
    df = df[df[TARGET] >= 0].copy()

    numeric_cols = [
        "avg_price",
        "avg_regular_price",
        "avg_discount_pct",
        "promo_intensity",
        "avg_starting_inventory",
        "holiday_days_in_week",
        "payday_days_in_week",
        "weekend_days_in_week",
        "black_friday_week",
        "month",
        "month_calendar",
        "promo_days_in_week",
        "avg_weekly_discount_pct",
        "has_promo_week",
        "week",
        "year",
        "quarter",
        "week_of_year",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "season" in df.columns:
        df["season"] = df["season"].fillna("unknown")

    promo_type_cols = [c for c in df.columns if c.startswith("promo_type_")]
    for col in promo_type_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# -----------------------------
# Feature engineering
# -----------------------------
def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["store_id", "product_id", "week_start"]).copy()

    group_cols = ["store_id", "product_id"]

    df["lag_1"] = df.groupby(group_cols)[TARGET].shift(1)
    df["lag_4"] = df.groupby(group_cols)[TARGET].shift(4)

    df["rolling_mean_4"] = (
        df.groupby(group_cols)[TARGET]
        .shift(1)
        .rolling(4)
        .mean()
    )

    return df


# -----------------------------
# Build next-week rows
# -----------------------------
def build_future_rows(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["store_id", "product_id", "week_start"]).copy()

    last_date = df["week_start"].max()
    next_week = last_date + pd.Timedelta(days=7)

    print(f"Last available week: {last_date}")
    print(f"Forecasting next week: {next_week}")

    latest = df.groupby(["store_id", "product_id"], as_index=False).last()

    future = latest.copy()
    future["week_start"] = next_week
    future["year"] = next_week.year
    future["week"] = int(next_week.isocalendar().week)

    # Basic future assumptions
    # You can improve these later with planned promo / price inputs
    if "promo_days_in_week" in future.columns:
        future["promo_days_in_week"] = 0
    if "avg_weekly_discount_pct" in future.columns:
        future["avg_weekly_discount_pct"] = 0
    if "has_promo_week" in future.columns:
        future["has_promo_week"] = 0

    promo_type_cols = [c for c in future.columns if c.startswith("promo_type_")]
    for col in promo_type_cols:
        future[col] = 0

    # Keep only rows with enough history
    future = future.dropna(subset=["lag_1", "lag_4", "rolling_mean_4"]).copy()

    return future


# -----------------------------
# Encode + align to model
# -----------------------------
def encode_and_align(future: pd.DataFrame, model) -> pd.DataFrame:
    future_encoded = pd.get_dummies(
        future,
        columns=["season", "store_id", "product_id"],
        drop_first=True
    )

    model_features = model.feature_names_in_

    for col in model_features:
        if col not in future_encoded.columns:
            future_encoded[col] = 0

    future_encoded = future_encoded[model_features].copy()

    for col in future_encoded.columns:
        if future_encoded[col].dtype == "bool":
            future_encoded[col] = future_encoded[col].astype(int)
        elif future_encoded[col].dtype == "object":
            future_encoded[col] = pd.to_numeric(
                future_encoded[col], errors="coerce"
            ).fillna(0)

    return future_encoded


# -----------------------------
# Save forecast
# -----------------------------
def save_forecast(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        old = pd.read_csv(path)

        if "week_start" in old.columns:
            old["week_start"] = pd.to_datetime(old["week_start"], errors="coerce")
        if "forecast_created_at" in old.columns:
            old["forecast_created_at"] = pd.to_datetime(
                old["forecast_created_at"], errors="coerce"
            )

        df = pd.concat([old, df], ignore_index=True)

        df = df.drop_duplicates(
            subset=["week_start", "store_id", "product_id", "model_version"],
            keep="last"
        )

    df.to_csv(path, index=False)
    print(f"\nForecast saved to: {path}")


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    print("Loading latest processed dataset...")
    df = load_data(DATA_PATH)

    print("Preparing data...")
    df = prepare_data(df)

    print("Creating lag features...")
    df = create_features(df)

    print("Loading best model...")
    model = load_model(BEST_MODEL_PATH)

    print("Building future rows...")
    future = build_future_rows(df)

    print("Encoding and aligning features...")
    X_future = encode_and_align(future, model)

    print("Generating predictions...")
    future["predicted_units"] = model.predict(X_future)

    forecast_output = future[[
        "week_start",
        "store_id",
        "product_id",
        "predicted_units"
    ]].copy()

    forecast_output["forecast_created_at"] = pd.Timestamp.today().normalize()
    forecast_output["model_version"] = MODEL_VERSION

    print("\nForecast preview:")
    print(forecast_output.head())

    print("\nSaving forecast...")
    save_forecast(forecast_output, FORECAST_PATH)


if __name__ == "__main__":
    main()