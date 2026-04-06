# build_weekly_actuals.py

import os
import warnings

import pandas as pd
import psycopg2

warnings.filterwarnings("ignore")


# -----------------------------
# Config
# -----------------------------
DB_CONFIG = {
    "host": "localhost",
    "database": "sunnybest_sfs",
    "user": "bonaventure",
    "password": ""
}

QUERY = """
SELECT
    date,
    store_id,
    product_id,
    units_sold
FROM core.fact_sales
"""

OUTPUT_PATH = "data/outputs/weekly_actuals.csv"


# -----------------------------
# Load data
# -----------------------------
def load_data_from_db() -> pd.DataFrame:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        df = pd.read_sql(QUERY, conn)
    finally:
        conn.close()
    return df


# -----------------------------
# Prepare data
# -----------------------------
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["store_id"] = df["store_id"].astype(str)
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce").astype("Int64")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")

    df = df.dropna(subset=["date", "store_id", "product_id", "units_sold"])
    df["product_id"] = df["product_id"].astype(int)

    df = df[df["units_sold"] >= 0].copy()

    return df


# -----------------------------
# Build weekly actuals
# -----------------------------
def build_weekly_actuals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Monday as week start
    df["week_start"] = df["date"] - pd.to_timedelta(df["date"].dt.weekday, unit="d")

    weekly_actuals = df.groupby(
        ["week_start", "store_id", "product_id"],
        as_index=False
    ).agg(
        actual_units=("units_sold", "sum")
    )

    weekly_actuals = weekly_actuals.sort_values(
        ["week_start", "store_id", "product_id"]
    ).reset_index(drop=True)

    return weekly_actuals


# -----------------------------
# Save output
# -----------------------------
def save_output(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    print("Loading sales data from PostgreSQL...")
    df = load_data_from_db()

    print("Preparing sales data...")
    df = prepare_data(df)

    print("Building weekly actuals...")
    weekly_actuals = build_weekly_actuals(df)

    print("Saving weekly actuals...")
    save_output(weekly_actuals, OUTPUT_PATH)

    print(f"\nWeekly actuals saved to: {OUTPUT_PATH}")
    print(f"Rows: {len(weekly_actuals):,}")
    print("\nPreview:")
    print(weekly_actuals.head())


if __name__ == "__main__":
    main()