# 📊 SunnyBest Forecasting System (SFS) – Forecasting Framework

---

## 🎯 Overview

The SunnyBest Forecasting System (SFS) is designed to predict future product demand to support both:

- **Strategic planning (quarterly)**
- **Short-term retail operations (weekly)**

The system enables the business to answer:

> *“How many units of each product will each store sell over the upcoming period, so we can plan inventory, reduce stockouts, and optimise operations?”*

---

## 🧠 Business Forecasting Objective

SFS supports **inventory planning through demand forecasting**, enabling:

- Stock planning and procurement  
- Replenishment decisions  
- Promotion optimisation  
- Operational workload planning  
- Revenue and budgeting forecasts  

A typical business request is:

> *“We are planning inventory for the next 4 weeks. Can you forecast weekly sales for each store so we know how much stock to order?”*

---

## 🎯 Primary Forecast Target

### Target Variable
- **`units_sold`**

### Definition
The number of units of a product sold at a given store on a given day.

---

## 📦 Modelling Grain (Data Science Layer)

> **`date × store_id × product_id`**

This is the core modelling unit used for:
- training models  
- generating predictions  
- capturing fine-grained demand patterns  

---

## 📊 Planning Grain (Business Layer)

> **`store_id × product_id × week`**

Although predictions are generated at **daily level**, they are typically:

- aggregated to **weekly level**
- used in **multi-week planning windows**

This ensures:
- high model accuracy (from granular data)
- practical usability (for business decisions)

---

## 🔁 Dual Forecasting Framework

The system operates two complementary forecasting cycles:

---

### 1. 📆 Quarterly Planning Forecast (Strategic)

#### Purpose
Supports:
- inventory procurement  
- budgeting and revenue planning  
- promotion and commercial strategy  
- seasonal preparation  

#### Timing
Produced four times a year:
- March  
- June  
- September  
- December  

#### Forecast Horizon
- **Next 12 weeks**

#### Output
- Weekly forecasts of `units_sold`
- At **store × product level**

#### Business Value
Provides a **medium-term demand outlook** for strategic decision-making.

---

### 2. 📅 Weekly Rolling Forecast (Operational)

#### Purpose
Supports:
- short-term replenishment  
- reacting to demand changes  
- identifying fast/slow-moving products  
- store-level operational decisions  

#### Timing
- Produced **every week**

#### Forecast Horizon
- **Next 4 weeks (rolling)**

#### Output
- Weekly forecasts of `units_sold`
- At **store × product level**

#### Business Value
Enables **fast, responsive operational adjustments**.

---

## ⏳ Flexible Forecast Horizons

In addition to structured planning cycles, the system supports flexible forecast horizons:

| Horizon | Description | Use Case |
|--------|------------|----------|
| 1 day ahead | Short-term forecast | Daily replenishment |
| 7 days ahead | Weekly planning | Inventory & staffing |
| 14 days ahead | Mid-term planning | Promotions & logistics |
| 28+ days ahead | Strategic planning | Procurement & budgeting |

---

## 📊 Forecast Levels and Aggregation

### Base Level (Model Output)
- Store × Product × Date

### Aggregated Outputs (User-Facing)

Forecasts can be aggregated into:

- Weekly demand per store  
- Weekly demand per store-product  
- Multi-week planning demand (4, 8, 12 weeks)  
- Regional or category-level demand  

---

## 🔄 User-Driven Forecast Workflow

### Step 1 – Input
- User uploads a CSV file containing base data (sales, inventory, etc.)

### Step 2 – Data Processing
- Data is validated and transformed into modelling dataset  
- Feature engineering is applied  

### Step 3 – Forecast Generation
- Model predicts **daily `units_sold`**

### Step 4 – Aggregation
- Predictions are aggregated into:
  - weekly forecasts  
  - multi-week planning windows  

### Step 5 – Planning Output
Outputs include:
- forecast demand  
- inventory gap  
- recommended stock to order  

---

## 📈 Derived Targets

Derived from `units_sold`:

| Target | Description |
|------|------------|
| revenue | units_sold × price |
| stockout_risk | Probability of stock depletion |
| demand_gap | Forecast demand − available inventory |
| service_pressure | Demand relative to operational capacity |

---

## 🧠 Modelling Approach

### Models
- Baseline models (moving averages, seasonal naive)  
- Statistical models (ARIMA, Prophet)  
- Machine learning models (XGBoost, LightGBM)  

### Feature Inputs
- Lag features  
- Rolling statistics  
- Promotions  
- Pricing  
- Weather  
- Calendar effects  
- Inventory signals  
- Customer behaviour  
- Operational workload  

---

## 🔁 Backtesting Framework

Forecasts are evaluated using **rolling origin backtesting**:

- Train on historical data  
- Predict future periods  
- Roll forward and repeat  

---

## 📏 Evaluation Metrics

| Metric | Purpose |
|------|--------|
| RMSE | Measures error magnitude |
| MAE | Measures average error |
| WAPE | Measures relative error |
| Bias | Detects systematic over/under prediction |

---

## ⚙️ Forecast Constraints and Adjustments

### Business Constraints
- Discount caps  
- Store constraints  
- Policy multipliers  

### Operational Constraints
- Inventory limits  
- Stock availability  

---

## 🔗 Integration with System Modules

| Module | Role |
|------|------|
| Data | Provides modelling dataset |
| Features | Builds predictive inputs |
| Forecasting | Generates predictions |
| Inventory | Uses forecasts for stock decisions |
| Pricing | Uses forecasts for elasticity |
| Planning | Uses forecasts for scenarios |
| AI | Explains forecasts |
| Monitoring | Tracks forecast performance |

---

## 📤 Output and Consumption

Forecast outputs are consumed by:

- `src/api/routes/predict.py` → API predictions  
- `src/dashboard/streamlit_app.py` → visualisation  
- `monitoring/` → performance tracking  
- Planning modules → scenario analysis  

---

## 📌 Key Assumptions

Demand is influenced by:

- Seasonality  
- Promotions  
- Pricing  
- Weather  
- Customer behaviour  

Additionally:
- Historical data is assumed to be reasonably representative of future demand patterns  

---

## 🚀 Key Advantage

The SFS forecasting framework combines:

- **Granular modelling (daily level)**  
- **Flexible aggregation (weekly & multi-period)**  
- **Structured planning cycles (quarterly & weekly)**  
- **Rich feature engineering**  
- **Integration with decision-making systems**  

This ensures forecasts are not just predictions, but:

> **Actionable decision-support tools for inventory and retail planning**

---

## ✅ Final Summary

| Component                | Description                                      |
|-------------------------|--------------------------------------------------|
| Target Variable         | `units_sold`                                     |
| Modelling Grain         | date × store_id × product_id                     |
| Planning Grain          | store_id × product_id × week                     |
| Quarterly Forecast      | Every quarter (March, June, Sept, Dec)           |
| Quarterly Horizon       | 12 weeks                                         |
| Weekly Forecast         | Every week                                       |
| Weekly Horizon          | 4 weeks                                          |
| Model Strategy          | One engine, multiple horizons                    |
| Business Objective      | Inventory planning & operational optimisation    |