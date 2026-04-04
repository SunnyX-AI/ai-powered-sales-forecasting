"""
train_units_forecast.py

Train and save the units_sold forecasting model for SunnyBest.
"""

from __future__ import annotations

from pathlib import Path
import joblib
import pandas as pd

from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error

# project imports
from data.make_weekly_dataset import build_merged_dataset
from src.features.build_features import build_forecast_features


# -----------------------------
# Config
# -----------------------------
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "xgb_units_forecast.pkl"
FEATURES_PATH = MODEL_DIR / "xgb_units_forecast_features.pkl"
METRICS_PATH = MODEL_DIR / "xgb_units_forecast_metrics.pkl"

RANDOM_STATE = 42
TARGET = "units_sold"


# -----------------------------
# Training
# -----------------------------
def train_units_forecast_model() -> dict:
    """
    Train units_sold forecast model and save artifacts.
    Returns training metrics.
    """

    # Load merged dataset
    df = build_merged_dataset(save=False)

    # Ensure time order for forecasting
    df = df.sort_values("date").reset_index(drop=True)

    # Build features
    X, y = build_forecast_features(df, target=TARGET)

    # Time-based split
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

    # Model
    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=RANDOM_STATE
    )

    # Fit
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_val)
    mse = mean_squared_error(y_val, preds)
    rmse = mse ** 0.5

    # Save model + feature columns + metrics
    joblib.dump(model, MODEL_PATH)
    joblib.dump(list(X.columns), FEATURES_PATH)
    joblib.dump(
        {
            "target": TARGET,
            "rmse": rmse,
            "n_train": len(X_train),
            "n_val": len(X_val),
            "n_features": X.shape[1],
        },
        METRICS_PATH,
    )

    print(f"✅ Units forecast model saved to: {MODEL_PATH}")
    print(f"✅ Feature columns saved to: {FEATURES_PATH}")
    print(f"✅ Metrics saved to: {METRICS_PATH}")
    print(f"📉 Validation RMSE: {rmse:,.2f}")

    return {
        "target": TARGET,
        "rmse": rmse,
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_features": X.shape[1],
    }


# -----------------------------
# CLI entry
# -----------------------------
if __name__ == "__main__":
    metrics = train_units_forecast_model()
    print("Training summary:", metrics)