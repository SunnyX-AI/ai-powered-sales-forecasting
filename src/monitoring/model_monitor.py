# monitor_model.py

import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# -----------------------------
# Config
# -----------------------------
FORECAST_PATH = "data/outputs/weekly_forecasts.csv"
ACTUALS_PATH = "data/processed/weekly_sales_v4_promotions.csv"

OUTPUT_MONITOR_PATH = "data/outputs/weekly_model_monitoring.csv"
OUTPUT_WEEKLY_SUMMARY_PATH = "data/outputs/weekly_monitoring_summary.csv"

PLOT_WAPE_PATH = "data/outputs/plots/weekly_wape.png"
PLOT_ACTUAL_VS_PRED_PATH = "data/outputs/plots/weekly_actual_vs_predicted.png"


# -----------------------------
# Load Data
# -----------------------------
def load_forecasts(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["week_start"] = pd.to_datetime(df["week_start"], errors="coerce")
    df["store_id"] = df["store_id"].astype(str)
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["week_start", "store_id", "product_id", "predicted_units"])
    df["product_id"] = df["product_id"].astype(int)
    df["predicted_units"] = pd.to_numeric(df["predicted_units"], errors="coerce")
    return df


def load_actuals(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["week_start"] = pd.to_datetime(df["week_start"], errors="coerce")
    df["store_id"] = df["store_id"].astype(str)
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["week_start", "store_id", "product_id", "units_sold"])
    df["product_id"] = df["product_id"].astype(int)
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    return df[["week_start", "store_id", "product_id", "units_sold"]].copy()


# -----------------------------
# Merge and Error Metrics
# -----------------------------
def build_monitoring_table(
    forecasts: pd.DataFrame,
    actuals: pd.DataFrame
) -> pd.DataFrame:
    df = forecasts.merge(
        actuals,
        on=["week_start", "store_id", "product_id"],
        how="left"
    )

    df["abs_error"] = (df["units_sold"] - df["predicted_units"]).abs()
    df["signed_error"] = df["predicted_units"] - df["units_sold"]

    # Avoid divide-by-zero for row-level APE
    df["ape"] = df["abs_error"] / df["units_sold"].replace(0, np.nan)

    return df


def build_weekly_summary(df_monitor: pd.DataFrame) -> pd.DataFrame:
    weekly = df_monitor.groupby("week_start", as_index=False).agg(
        actual_sum=("units_sold", "sum"),
        predicted_sum=("predicted_units", "sum"),
        abs_error_sum=("abs_error", "sum"),
        bias_sum=("signed_error", "sum"),
        item_count=("product_id", "count"),
    )

    weekly["WAPE"] = weekly["abs_error_sum"] / weekly["actual_sum"].replace(0, np.nan)
    weekly["BIAS_PCT"] = weekly["bias_sum"] / weekly["actual_sum"].replace(0, np.nan)

    weekly["alert"] = weekly["WAPE"].apply(
        lambda x: "Check Model" if pd.notna(x) and x > 0.20 else "OK"
    )

    return weekly


# -----------------------------
# Save Outputs
# -----------------------------
def save_csv(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


# -----------------------------
# Plotting
# -----------------------------
def plot_wape(weekly: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(weekly["week_start"], weekly["WAPE"], marker="o")
    plt.title("Weekly Forecast WAPE Over Time")
    plt.xlabel("Week")
    plt.ylabel("WAPE")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def plot_actual_vs_predicted(weekly: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(weekly["week_start"], weekly["actual_sum"], marker="o", label="Actual")
    plt.plot(weekly["week_start"], weekly["predicted_sum"], marker="o", label="Predicted")
    plt.title("Actual vs Predicted Weekly Units")
    plt.xlabel("Week")
    plt.ylabel("Units Sold")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


# -----------------------------
# Overall Metrics
# -----------------------------
def print_overall_metrics(df_monitor: pd.DataFrame) -> None:
    overall_mae = df_monitor["abs_error"].mean()
    overall_wape = df_monitor["abs_error"].sum() / df_monitor["units_sold"].sum()
    overall_bias = df_monitor["signed_error"].sum() / df_monitor["units_sold"].sum()

    print("\nOverall Monitoring Metrics")
    print("-" * 30)
    print(f"Overall MAE:     {overall_mae:.4f}")
    print(f"Overall WAPE:    {overall_wape:.4%}")
    print(f"Overall Bias %:  {overall_bias:.4%}")


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    print("Loading forecasts...")
    forecasts = load_forecasts(FORECAST_PATH)

    print("Loading actuals...")
    actuals = load_actuals(ACTUALS_PATH)

    print("Building monitoring table...")
    df_monitor = build_monitoring_table(forecasts, actuals)

    print("Building weekly summary...")
    weekly_summary = build_weekly_summary(df_monitor)

    print("Saving outputs...")
    save_csv(df_monitor, OUTPUT_MONITOR_PATH)
    save_csv(weekly_summary, OUTPUT_WEEKLY_SUMMARY_PATH)

    print("Creating plots...")
    plot_wape(weekly_summary, PLOT_WAPE_PATH)
    plot_actual_vs_predicted(weekly_summary, PLOT_ACTUAL_VS_PRED_PATH)

    print_overall_metrics(df_monitor)

    print("\nSaved files:")
    print(f"- Monitoring table: {OUTPUT_MONITOR_PATH}")
    print(f"- Weekly summary:   {OUTPUT_WEEKLY_SUMMARY_PATH}")
    print(f"- WAPE plot:        {PLOT_WAPE_PATH}")
    print(f"- Actual vs Pred:   {PLOT_ACTUAL_VS_PRED_PATH}")

    print("\nWeekly Summary Preview:")
    print(weekly_summary.head())


if __name__ == "__main__":
    main()