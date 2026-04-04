# SunnyBest Forecasting System (SFS) – Modules Overview

The SunnyBest Forecasting System (SFS) is an end-to-end **forecasting and operational intelligence platform** designed to support retail decision-making.

This document describes the core system modules and maps them directly to the project architecture, ensuring alignment between business functionality and implementation.

---

## 1. Demand Forecasting

Forecast future demand at store-product level to support planning and operations.

### System Components
- `src/forecasting/train.py`
- `src/forecasting/predict.py`
- `src/forecasting/evaluate.py`
- `src/forecasting/backtest.py`
- `src/forecasting/pipelines.py`

### Data Dependencies
- `data/raw/transactions/sunnybest_sales.csv`
- `data/raw/foundation/sunnybest_calendar.csv`
- `data/raw/foundation/sunnybest_weather.csv`
- Feature tables from `src/features/`

### Key Capabilities
- Units sold prediction
- Revenue forecasting
- Multi-horizon forecasting (daily, weekly, monthly)
- Store-product level modelling

### Outputs
- Forecasts stored in `models/` and `monitoring/`
- Exposed via API (`src/api/routes/predict.py`)
- Used by dashboard and planning modules

---

## 2. Store Intelligence

Analyse store performance and identify operational issues.

### System Components
- `src/operations/kpis.py`
- `src/operations/service_metrics.py`
- `src/operations/workload_analysis.py`

### Data Dependencies
- Sales data
- Store metadata (`sunnybest_stores.csv`)
- Operational data (`sunnybest_store_operations.csv`)

### Key Capabilities
- Store performance tracking
- Regional comparisons
- KPI monitoring

### Outputs
- KPIs for dashboard (`src/dashboard/streamlit_app.py`)
- Inputs to risk and alert systems

---

## 3. Promotions Impact

Evaluate how promotions influence demand and revenue.

### System Components
- `src/features/promo_features.py`
- `src/pricing/build_elasticity.py`
- `src/pricing/elasticity.py`

### Data Dependencies
- `sunnybest_promotions.csv`
- Sales data

### Key Capabilities
- Promotion uplift modelling
- Discount impact analysis
- ROI estimation

### Outputs
- Features for forecasting models
- Inputs to scenario simulation

---

## 4. Inventory Intelligence

Monitor stock levels and optimise replenishment decisions.

### System Components
- `src/inventory/stockout_model.py`
- `src/inventory/replenishment.py`
- `src/inventory/service_level.py`

### Data Dependencies
- `sunnybest_inventory.csv`
- Forecast outputs

### Key Capabilities
- Stockout prediction
- Replenishment planning
- Overstock detection

### Outputs
- Risk scores
- Alerts
- Replenishment recommendations

---

## 5. External Drivers

Incorporate external signals into forecasting and analysis.

### System Components
- `src/features/calendar_features.py`
- `src/features/demand_features.py`

### Data Dependencies
- Weather data
- Calendar data

### Key Capabilities
- Seasonality modelling
- Weather impact analysis
- Event effects

---

## 6. Business Rules Layer (Policy Engine)

Apply business constraints and operational rules.

### System Components
- `src/policy/policy_engine.py`
- `src/policy/constraint_application.py`

### Data Dependencies
- `sunnybest_policy_regimes.csv`
- `sunnybest_restriction_events.csv`

### Key Capabilities
- Enforce stock constraints
- Apply promotion rules
- Adjust outputs based on policy

### Role in System
Ensures model outputs are aligned with real-world constraints.

---

## 7. AI Assistant (GenAI Layer)

Provide natural language access to forecasts and insights.

### System Components
- `src/ai/copilot.py`
- `src/ai/services/assistant.py`
- `src/ai/rag/`

### Data Dependencies
- `docs/` (knowledge base)
- Forecast outputs
- Monitoring data

### Key Capabilities
- Question answering
- Insight generation
- RAG-based explanations

### Outputs
- API endpoint (`src/api/routes/ai.py`)
- Integrated into dashboard

---

## 8. Risk & Alerts System

Detect anomalies and trigger alerts.

### System Components
- `src/monitoring/metrics.py`
- `src/monitoring/drift.py`
- `src/monitoring/rules.py`

### Data Dependencies
- Forecast outputs
- Historical data

### Key Capabilities
- Drift detection
- Threshold alerts
- Anomaly detection

### Outputs
- `monitoring/*.csv`
- Alerts for dashboard/API

---

## 9. Segmentation Layer

Group entities for deeper analysis.

### System Components
- `src/features/`
- Custom clustering workflows

### Key Capabilities
- Customer segmentation
- Product clustering
- Store grouping

### Outputs
- Features for modelling
- Inputs to AI and planning modules

---

## 10. Scenario Simulation

Enable "what-if" analysis for decision-making.

### System Components
- `src/planning/scenario_engine.py`
- `src/planning/what_if.py`
- `src/planning/plan_generation.py`

### Data Dependencies
- Forecast outputs
- Pricing and promotion data

### Key Capabilities
- Price simulations
- Promotion testing
- Demand sensitivity analysis

### Outputs
- Scenario forecasts
- Decision support outputs

---

## System Integration Layer

### API
- `src/api/app.py`
- Routes:
  - Forecasting
  - AI assistant
  - Monitoring

### Dashboard
- `src/dashboard/streamlit_app.py`

### Data Pipeline
- `src/data/make_dataset.py`
- `src/features/build_features.py`

---

## System Summary

The SFS is a **modular, production-style forecasting intelligence platform** that integrates:

- Forecasting models
- Operational analytics
- Policy constraints
- AI-driven insights
- Monitoring and governance

Each module is directly mapped to system components, ensuring full alignment between business logic and implementation.