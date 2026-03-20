# SunnyBest Forecasting System (SFS) – Modules Overview

This document outlines the core and advanced modules of the SFS platform.
It serves as a reference point for development, feature expansion, and system design.

---

## 1. Demand Forecasting
Predict future sales across different dimensions.

**Key Features:**
- Units sold prediction
- Revenue forecasting
- Time-series modelling (daily/weekly/monthly)
- Store-product level forecasting

**Techniques:**
- XGBoost / LightGBM
- ARIMA / Prophet
- Feature engineering (lags, rolling averages)

---

## 2. Store Intelligence
Analyse and monitor store performance.

**Key Features:**
- Store-level performance metrics
- Regional comparisons
- Identification of underperforming stores
- KPI dashboards

---

## 3. Promotions Impact
Evaluate how promotions affect sales.

**Key Features:**
- Discount impact analysis
- Promotion uplift modelling
- Campaign effectiveness tracking
- ROI of promotions

---

## 4. Inventory Intelligence
Optimise stock levels and reduce stock-related issues.

**Key Features:**
- Stock level monitoring
- Stockout prediction
- Replenishment recommendations
- Overstock detection

---

## 5. External Drivers
Incorporate external factors into forecasting.

**Key Features:**
- Weather impact analysis
- Holiday and event effects
- Seasonality patterns
- Economic indicators (optional)

---

## 6. Business Rules Layer (Policy Engine)
Apply business constraints and operational rules.

**Key Features:**
- Minimum/maximum stock rules
- Promotion eligibility rules
- Store-specific constraints
- Operational policies

**Analogy:**
- Similar to “Sanctions” in Universal Credit systems
- Enforces rules that influence outcomes

---

## 7. AI Assistant (GenAI Layer)
Enable natural language interaction with the system.

**Key Features:**
- Ask questions about data:
  - "Why did sales drop last week?"
  - "Which stores will underperform next month?"
- Automated insights generation
- RAG (Retrieval-Augmented Generation) + LangChain layer


---

## 8. Risk & Alerts System
Detect issues early and notify stakeholders.

**Key Features:**
- Low stock alerts
- Forecast anomalies detection
- Sudden sales drop alerts
- Threshold-based notifications

**Business Value:**
- Prevents revenue loss
- Improves operational response

---

## 9. Segmentation Layer
Group entities for better analysis and targeting.

**Key Features:**
- Customer segmentation (RFM)
- Product clustering
- Store categorisation
- Behavioural grouping

---

## 10. Scenario Simulation
Enable decision-making through "what-if" analysis.

**Key Features:**
- Price change simulations
- Promotion scenario testing
- Demand sensitivity analysis
- Forecast under different conditions

**Example Questions:**
- What happens if price increases by 10%?
- What if a promotion is applied next week?
- How will demand change with weather variation?

---

## 🧠 Summary

The SFS is not just a forecasting model — it is an **intelligent decision-support system** combining:

- Predictive Analytics
- Business Rules
- AI Insights
- Operational Monitoring

This modular structure ensures scalability, maintainability, and real-world applicability.