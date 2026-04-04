# 📊 SunnyBest Forecasting System (SFS) — Modelling Documentation

## 🎯 Overview

This document summarises the modelling approach used to forecast **weekly `units_sold`** in the SunnyBest Forecasting System (SFS), including:

* Assumptions
* Strengths
* Limitations
* Key Insights
* Design Decisions

The goal of the model is to support:

* **Weekly operational planning (4-week horizon)**
* **Quarterly strategic planning (12-week horizon)**

---

# 🧠 Modelling Approach

## Target

* `units_sold` (aggregated weekly)
* Grain:
  year × week × store_id × product_id

---

## Model Type

* Primary model: **RandomForestRegressor**
* Approach:

  * Supervised learning
  * Time-aware feature engineering
  * No random shuffling (time-based split)

---

## Train/Test Strategy

* Training data: **Before 2026**
* Test data: **2026 onward**
* Purpose:

  * Simulates real-world forecasting
  * Prevents data leakage

---

# 🏗️ Feature Engineering Summary

## Time-Based Features

* `lag_1`
* `lag_4`
* `rolling_mean_4`

## Sales-Derived Features

* `avg_price`
* `avg_regular_price`
* `avg_discount_pct`
* `promo_intensity`
* `avg_starting_inventory`

## Calendar Features

* `holiday_days_in_week`
* `payday_days_in_week`
* `weekend_days_in_week`
* `black_friday_week`
* `month`, `quarter`, `week_of_year`
* `season`

## Promotion Features

* `promo_days_in_week`
* `avg_weekly_discount_pct`
* `has_promo_week`
* `promo_type_*` (one-hot encoded)

---

# 📈 Model Performance

* Mean Weekly Units: ~15.77
* MAE: ~2.36
* WAPE: ~15%

### Interpretation

* Model error ≈ **2–3 units per week**
* Performance considered **strong for retail demand forecasting**

---

# 💪 Strengths

## 1. Strong Predictive Performance

* Achieved ~15% WAPE from ~34% baseline
* Significant improvement through feature engineering

## 2. Realistic Evaluation Strategy

* Time-based split mimics production usage
* Avoids future data leakage

## 3. Feature-Rich Modelling

* Combines:

  * historical demand
  * pricing
  * promotions
  * calendar effects

## 4. Scalable Pipeline Design

* Clear separation:
  data pipeline → model pipeline
* Easily extendable with new datasets

## 5. Business Alignment

* Weekly aggregation aligns with:

  * inventory planning
  * operational decision-making

---

# ⚠️ Limitations

## 1. Heavy Dependence on Historical Demand

Feature importance shows:

rolling_mean_4 ≈ dominant driver

Implication:

* Model is highly **autoregressive**
* Relies heavily on past sales patterns

## 2. Limited Causal Understanding

* Promotions and calendar features have low importance
* Model may not fully capture:

  * causal drivers
  * sudden demand shocks

## 3. Reactive Rather Than Proactive

* Performs well when:
  future ≈ recent past
* May struggle with:

  * new promotions
  * policy changes
  * unexpected demand shifts

## 4. Feature Leakage Risk (Potential)

* Rolling and lag features must be carefully constructed
* Incorrect implementation could leak future information

## 5. No Hyperparameter Optimisation

* Model uses default RandomForest parameters
* Performance may be improved with tuning

---

# 🧠 Key Assumptions

## 1. Temporal Stability

* Assumes demand patterns are relatively stable over short periods

## 2. Historical Demand is Predictive

* Past sales (lags, rolling averages) are strong predictors of future demand

## 3. Weekly Aggregation is Sufficient

* Daily variation is intentionally smoothed out
* Assumes weekly trends are adequate for planning

## 4. Promotions Already Reflected in Sales

* Some promotional effects are implicitly captured in historical demand

## 5. Data Quality is Reliable

* Assumes:

  * correct inventory records
  * accurate pricing and promotion data

---

# ⚖️ Weaknesses

## 1. Over-reliance on Rolling Features

* `rolling_mean_4` dominates (~95% importance)
* Reduces contribution of other meaningful features

## 2. Limited Interpretability

* Tree-based ensemble models are less interpretable than linear models

## 3. Sparse Promotion Data

* Promotions dataset is relatively small
* Limits its impact on model learning

## 4. No External Drivers Yet

* Weather, customer behaviour, and macro effects not included

---

# 🔍 Key Insights

## 1. Feature Engineering > Model Choice

* Largest improvements came from:

  * calendar features
  * structured aggregation
* Not from switching algorithms

## 2. Diminishing Returns

* Promotions added only marginal improvement
* Indicates earlier features already captured key signals

## 3. Strong Baseline Achieved

* Model is already suitable for:

  * operational forecasting
  * initial production deployment

---

# 🚀 Future Improvements

## Short-Term

* Reduce dominance of `rolling_mean_4`
* Improve promotion feature representation
* Try alternative models (e.g. XGBoost)

## Medium-Term

* Add external datasets:

  * weather
  * customer activity
  * store operations

## Long-Term

* Build hybrid models:

  * statistical + ML
* Introduce probabilistic forecasting
* Incorporate uncertainty estimation

---

# 🧾 Final Summary

The current weekly demand model:

* is **accurate (~15% WAPE)**
* is **production-ready as a first candidate**
* is **heavily driven by historical demand patterns**
* benefits significantly from structured feature engineering

It serves as a strong foundation for:

* inventory planning
* forecasting pipelines
* further model improvement

---
