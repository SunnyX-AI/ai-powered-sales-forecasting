# SunnyBest Forecasting System (SFS) – Methodology

This document describes the end-to-end methodology used in the SunnyBest Forecasting System (SFS), from raw data ingestion to forecast generation and business outputs.

The methodology ensures that forecasts are:

- Accurate  
- Scalable  
- Explainable  
- Aligned with real-world retail decision-making  

---

## 1. System Overview

The forecasting pipeline follows a structured flow:

Raw Data → Data Integration → Feature Engineering → Model Training → Prediction → Aggregation → Planning Output

Each stage is modular and implemented within the `src/` architecture.

---

## 2. Data Ingestion

### Sources

Data is loaded from:

- data/raw/foundation/  
- data/raw/transactions/  
- data/raw/behaviour_operations/  
- data/raw/policy_constraints/  

### Implementation

- src/data/loaders.py  

### Key Activities

- Load CSV files into dataframes  
- Standardise column names and formats  
- Validate schema consistency  

---

## 3. Data Integration (Joins)

### Objective

Combine all datasets into a single modelling dataset.

### Implementation

- src/data/joins.py  
- src/data/make_dataset.py  

### Process

1. Start with sales (fact table)  
2. Join stores and products  
3. Join calendar features  
4. Join weather data (via city)  
5. Join promotions  
6. Join inventory  
7. Join customer activity  
8. Join store operations  

### Output

- Cleaned dataset stored in data/processed/  

---

## 4. Data Validation and Quality Checks

### Implementation

- src/validation/schema_checks.py  
- src/validation/data_quality.py  
- src/validation/business_rules.py  

### Checks

- Missing values  
- Duplicates  
- Invalid keys  
- Logical inconsistencies (e.g. negative sales)  

---

## 5. Feature Engineering

### Objective

Transform raw data into predictive features.

### Implementation

- src/features/build_features.py  

### Feature Modules

- demand_features.py → lag features, rolling averages  
- calendar_features.py → seasonality, holidays  
- promo_features.py → promotion indicators  
- inventory_features.py → stock signals  
- operational_features.py → workload and service pressure  

### Key Features

- Lagged demand (t-1, t-7, t-14)  
- Rolling means (7-day, 14-day)  
- Promotion flags and discount intensity  
- Price-related features  
- Weather indicators  
- Customer activity metrics  
- Operational workload signals  

---

## 6. Model Training

### Objective

Train models to predict future demand.

### Implementation

- src/forecasting/train.py  

### Models Used

- Baseline models  
- ARIMA / Prophet  
- XGBoost / LightGBM  

### Training Strategy

- Train on historical data  
- Use feature matrix + target (units_sold)  
- Tune hyperparameters  

---

## 7. Backtesting and Evaluation

### Implementation

- src/forecasting/backtest.py  
- src/forecasting/evaluate.py  

### Approach

- Rolling origin backtesting  
- Evaluate across multiple time windows  

### Metrics

- RMSE  
- MAE  
- WAPE  
- Bias  

---

## 8. Prediction Pipeline

### Implementation

- src/forecasting/predict.py  
- src/forecasting/pipelines.py  

### Process

1. Load trained model  
2. Generate features for forecast horizon  
3. Predict units_sold at date × store × product level  

---

## 9. Forecast Aggregation

### Objective

Transform model outputs into business-ready forecasts.

### Process

- Aggregate daily predictions into:
  - Weekly demand  
  - Multi-week planning windows (4, 8, 12, 52 weeks)  

### Output Examples

- Weekly demand per store  
- Weekly demand per store-product  
- Total demand over planning horizon  

---

## 10. Inventory Planning Logic

### Objective

Convert forecasts into actionable stock decisions.

### Implementation

- src/inventory/replenishment.py  
- src/inventory/stockout_model.py  

### Logic

Recommended Order = Forecast Demand − Current Inventory

### Outputs

- Stock requirements  
- Stockout risk  
- Inventory gap  

---

## 11. Policy and Constraint Application

### Implementation

- src/policy/policy_engine.py  
- src/policy/constraint_application.py  

### Adjustments

- Apply business rules  
- Enforce constraints  
- Modify forecasts based on policy  

---

## 12. API Layer

### Implementation

- src/api/app.py  
- src/api/routes/predict.py  

### Workflow

1. User uploads CSV  
2. System processes data  
3. Forecast is generated  
4. Results returned via API  

---

## 13. Dashboard Integration

### Implementation

- src/dashboard/streamlit_app.py  

### Capabilities

- Visualise forecasts  
- Explore trends  
- View inventory recommendations  

---

## 14. Monitoring and Feedback Loop

### Implementation

- src/monitoring/metrics.py  
- src/monitoring/drift.py  

### Tracking

- Forecast accuracy  
- Model drift  
- Prediction logs  

---

## 15. AI Integration (GenAI Layer)

### Implementation

- src/ai/  
- src/ai/rag/  

### Capabilities

- Explain forecasts  
- Answer user queries  
- Generate insights  

---

## 16. End-to-End Workflow Summary

User uploads data  
→ Data is validated and integrated  
→ Features are generated  
→ Model predicts daily demand  
→ Forecasts are aggregated  
→ Inventory recommendations are computed  
→ Results are returned via API/dashboard  

---

## 17. Summary

The SFS methodology provides a complete forecasting pipeline, integrating:

- Data engineering  
- Feature engineering  
- Machine learning  
- Business rules  
- Operational decision logic  

This ensures forecasts are not only accurate, but also usable, interpretable, and actionable in real-world retail planning.