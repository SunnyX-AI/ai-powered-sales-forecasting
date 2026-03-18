"""
predict_units.py

Batch prediction interface for SunnyBest units_sold forecasting.

Purpose:
- Load saved units forecast model
- Build the same features used during training
- Align columns to training schema
- Predict units_sold for uploaded CSV / dataframe input
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import joblib
import pandas as pd

from src.features.build_features import build_forecast_features


MODEL_DIR = Path("models")
UNITS_MODEL_PATH = MODEL_DIR / "xgb_units_forecast.pkl"
UNITS_FEATURES_PATH = MODEL_DIR / "xgb_units_forecast_features.pkl"


REQUIRED_COLUMNS = [
    "date",
    "store_id",
    "product_id",
    "price",
    "regular_price",
    "discount_pct",
    "promo_flag",
    "month",
    "is_weekend",
    "is_holiday",
    "is_payday",
    "category",
    "store_size",
    "temperature_c",
    "rainfall_mm",
    "units_sold",   # needed for lag/rolling features with current feature pipeline
]


def load_units_model():
    """
    Load the trained units forecast model.
    """
    if not UNITS_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing units forecast model: {UNITS_MODEL_PATH}. "
            "Train it first using src/models/train_units_forecast.py"
        )
    return joblib.load(UNITS_MODEL_PATH)


def load_units_feature_columns() -> List[str]:
    """
    Load the feature column list used during training.
    """
    if not UNITS_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Missing feature columns file: {UNITS_FEATURES_PATH}. "
            "Train the units model first so feature columns are saved."
        )
    return joblib.load(UNITS_FEATURES_PATH)


def validate_units_input(df: pd.DataFrame) -> None:
    """
    Validate minimum required schema.
    """
    if df.empty:
        raise ValueError("Input dataframe is empty.")

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Input dataframe is missing required columns: {missing_cols}"
        )

    if "date" in df.columns:
        parsed_dates = pd.to_datetime(df["date"], errors="coerce")
        if parsed_dates.isna().all():
            raise ValueError("Column 'date' could not be parsed into valid datetimes.")


def align_to_training_columns(
    X_new: pd.DataFrame,
    trained_columns: List[str],
) -> pd.DataFrame:
    """
    Align new feature matrix to the columns seen during training.

    - add missing columns with 0
    - drop unexpected columns
    - preserve training order
    """
    X_aligned = X_new.copy()

    missing_cols = [c for c in trained_columns if c not in X_aligned.columns]
    for c in missing_cols:
        X_aligned[c] = 0

    extra_cols = [c for c in X_aligned.columns if c not in trained_columns]
    if extra_cols:
        X_aligned = X_aligned.drop(columns=extra_cols)

    return X_aligned[trained_columns]


def build_units_features_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reuse the training-time feature builder for units_sold prediction.

    Note:
    - Because the current feature engineering uses lag/rolling features
      derived from units_sold itself, the dataframe must contain units_sold
      so those historical features can be computed.
    - This works best for historical/batch scoring and planning datasets
      that include enough prior rows for lag creation.
    """
    df_work = df.copy()

    # Ensure date type is consistent
    df_work["date"] = pd.to_datetime(df_work["date"], errors="coerce")

    # Reuse training logic
    X, _ = build_forecast_features(df_work, target="units_sold")
    return X


def predict_units_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Predict units_sold from an input dataframe.

    Returns a CSV-ready dataframe containing the original rows used for prediction
    plus a `predicted_units_sold` column.
    """
    validate_units_input(df)

    model = load_units_model()
    trained_columns = load_units_feature_columns()

    df_work = df.copy()
    df_work["date"] = pd.to_datetime(df_work["date"], errors="coerce")

    # Build features using the same training logic
    X = build_units_features_for_prediction(df_work)

    # Align to training schema
    X = align_to_training_columns(X, trained_columns)

    # Because build_forecast_features drops rows with lag/rolling NaNs,
    # we need to rebuild the same valid-row mask to align predictions back
    # to the source dataframe.
    X_full, y_full = build_forecast_features(df_work, target="units_sold")
    valid_index = X_full.index

    preds = model.predict(X)

    result_df = df_work.loc[valid_index].copy()
    result_df["predicted_units_sold"] = preds

    return result_df.reset_index(drop=True)


def predict_units_from_csv(csv_path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file and return units_sold predictions.
    """
    df = pd.read_csv(csv_path)
    return predict_units_from_dataframe(df)


if __name__ == "__main__":
    # Example local sanity check
    sample_path = Path("data/processed/sample_units_input.csv")

    if sample_path.exists():
        output = predict_units_from_csv(sample_path)
        print("✅ Units forecast generated.")
        print(output.head())
    else:
        print(
            "ℹ️ No sample CSV found at data/processed/sample_units_input.csv. "
            "Use predict_units_from_dataframe(...) or predict_units_from_csv(...)."
        )