# make_weekly_dataset_v4_promotions.py

import os
import pandas as pd
import psycopg2


# -----------------------------
# Config
# -----------------------------
DB_CONFIG = {
    "host": "localhost",
    "database": "sunnybest_sfs",
    "user": "bonaventure",
    "password": ""
}

INPUT_PATH = "data/processed/weekly_sales_v3_calendar.csv"
OUTPUT_PATH = "data/processed/weekly_sales_v4_promotions.csv"
PROMOTIONS_QUERY = "SELECT * FROM core.fact_promotions"


# -----------------------------
# Load data
# -----------------------------
def load_weekly_v3(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_promotions() -> pd.DataFrame:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        promotions = pd.read_sql(PROMOTIONS_QUERY, conn)
    finally:
        conn.close()
    return promotions


# -----------------------------
# Prepare promotions
# -----------------------------
def prepare_promotions(promotions: pd.DataFrame) -> pd.DataFrame:
    promotions = promotions.copy()

    promotions["date"] = pd.to_datetime(promotions["date"], errors="coerce")
    promotions = promotions.dropna(subset=["date", "store_id", "product_id"])

    promotions["store_id"] = promotions["store_id"].astype(str)
    promotions["product_id"] = pd.to_numeric(
        promotions["product_id"], errors="coerce"
    ).astype("Int64")

    promotions = promotions.dropna(subset=["product_id"])
    promotions["product_id"] = promotions["product_id"].astype(int)

    promotions["promo_flag"] = pd.to_numeric(
        promotions["promo_flag"], errors="coerce"
    ).fillna(0).astype(int)

    promotions["discount_pct"] = pd.to_numeric(
        promotions["discount_pct"], errors="coerce"
    ).fillna(0)

    promotions["promo_type"] = promotions["promo_type"].fillna("No Promo")

    iso = promotions["date"].dt.isocalendar()
    promotions["year"] = iso.year.astype(int)
    promotions["week"] = iso.week.astype(int)

    return promotions


# -----------------------------
# Aggregate promotions weekly
# -----------------------------
def build_weekly_promo_features(promotions: pd.DataFrame) -> pd.DataFrame:
    promo_weekly = promotions.groupby(
        ["year", "week", "store_id", "product_id"],
        as_index=False
    ).agg(
        promo_days_in_week=("promo_flag", "sum"),
        avg_weekly_discount_pct=("discount_pct", "mean"),
        has_promo_week=("promo_flag", "max")
    )

    promo_type_dummies = pd.get_dummies(
        promotions["promo_type"],
        prefix="promo_type"
    )

    promotions_with_types = pd.concat(
        [
            promotions[["year", "week", "store_id", "product_id"]].reset_index(drop=True),
            promo_type_dummies.reset_index(drop=True)
        ],
        axis=1
    )

    promo_type_weekly = promotions_with_types.groupby(
        ["year", "week", "store_id", "product_id"],
        as_index=False
    ).max()

    promo_weekly = promo_weekly.merge(
        promo_type_weekly,
        on=["year", "week", "store_id", "product_id"],
        how="left"
    )

    return promo_weekly


# -----------------------------
# Merge datasets
# -----------------------------
def merge_datasets(
    df_weekly: pd.DataFrame,
    promo_weekly: pd.DataFrame
) -> pd.DataFrame:
    df = df_weekly.copy()

    df["store_id"] = df["store_id"].astype(str)
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["product_id"])
    df["product_id"] = df["product_id"].astype(int)

    df = df.merge(
        promo_weekly,
        on=["year", "week", "store_id", "product_id"],
        how="left"
    )

    df["promo_days_in_week"] = df["promo_days_in_week"].fillna(0)
    df["avg_weekly_discount_pct"] = df["avg_weekly_discount_pct"].fillna(0)
    df["has_promo_week"] = df["has_promo_week"].fillna(0)

    promo_type_cols = [c for c in df.columns if c.startswith("promo_type_")]
    for col in promo_type_cols:
        df[col] = df[col].fillna(0)

    return df


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
    print("Loading weekly v3 calendar dataset...")
    df_weekly = load_weekly_v3(INPUT_PATH)

    print("Loading promotions data...")
    promotions = load_promotions()

    print("Preparing promotions...")
    promotions = prepare_promotions(promotions)

    print("Building weekly promotion features...")
    promo_weekly = build_weekly_promo_features(promotions)

    print("Merging weekly dataset with promotions...")
    df_v4 = merge_datasets(df_weekly, promo_weekly)

    print("Saving weekly v4 dataset...")
    save_output(df_v4, OUTPUT_PATH)

    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Rows: {len(df_v4):,}")
    print(df_v4.head())


if __name__ == "__main__":
    main()