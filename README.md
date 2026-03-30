# 🧠 SunnyBest Forecasting System (SFS)  
## 📦 AI-Powered Demand, Inventory & Retail Intelligence Platform

An end-to-end **AI, Machine Learning, and Generative AI–driven forecasting system** built for a telecom and consumer electronics retailer.

The system transforms raw retail data into **forecast-driven inventory decisions**, enabling planners to answer:

> “How much stock should we order over the next 4–8 weeks?”

---

# 🚀 Key Capability

This system is designed around a **real-world business workflow**:

1. Upload retail data (CSV)  
2. Generate demand forecasts  
3. Aggregate forecasts into weekly planning windows  
4. Compute inventory gaps  
5. Recommend stock to order  

👉 Not just predictions — **decision-ready outputs**

---

# 🏗️ System Architecture

![SunnyBest SFS Architecture](assets/architecture.png)

---

## 📸 System Snapshot

### API (FastAPI)
![API Swagger Docs](assets/screenshots/swagger_docs.png)

### Dashboard (Streamlit)
![Streamlit Overview](assets/screenshots/streamlit_overview.png)

### Prediction Flow
![Streamlit Predict](assets/screenshots/streamlit_predict.png)

---

# 🎯 Project Aim

To build a **production-style forecasting intelligence system** that integrates:

- Demand forecasting  
- Inventory planning  
- Pricing & promotion analytics  
- Operational insights  
- Generative AI explanations  

---

# 🏪 Business Context

SunnyBest Telecommunications operates retail outlets across:

**Benin, Ekpoma, Auchi, Irrua, Igueben, Agenebode, Ogwa (Edo State, Nigeria)**

Key challenges addressed:

- Demand volatility and strong seasonal patterns  
- Stock-outs leading to lost revenue and poor customer experience  
- Uncertainty around promotion effectiveness and ROI  
- Pricing decisions affecting demand and profitability  
- Limited access to insights for non-technical stakeholders  

---

# 🧩 What This System Demonstrates

- ✔ Store-product level demand forecasting  
- ✔ Inventory planning and stock-out risk modelling  
- ✔ Promotion and pricing analytics  
- ✔ Scenario simulation (what-if analysis)  
- ✔ Generative AI (RAG) for explainable insights  
- ✔ Production-style architecture (API, Docker, modular design)  

---

# ⚙️ Methodology (End-to-End Pipeline)

```
Raw Data → Data Integration → Feature Engineering → Model Training → Prediction → Aggregation → Planning Output
```

### Core Flow

- Data is ingested and validated  
- Datasets are joined into a modelling dataset  
- Features are engineered (lags, promotions, pricing, weather, etc.)  
- Models predict **daily demand (units_sold)**  
- Forecasts are aggregated into:
  - Weekly demand  
  - Multi-week planning windows (4–52 weeks)  
- Inventory recommendations are generated:

```
Recommended Order = Forecast Demand − Current Inventory
```

👉 Outputs are delivered via API and dashboard

---

# 📊 Forecasting Design

- **Target:** units_sold  
- **Grain:** date × store × product  
- **Horizons:** 1 day → 52 weeks  
- **Aggregation:** daily → weekly → planning windows  

---

# 📦 Key Outputs

- Demand forecasts  
- Revenue projections  
- Stock-out risk indicators  
- Inventory gaps  
- Recommended stock orders  

---

# 🧠 Generative AI Layer

- Retrieval-Augmented Generation (RAG) over system knowledge  
- Natural language queries:
  - “Why did sales drop?”  
  - “Which stores are at risk?”  
- Insight summarisation for non-technical users  

---

# 📈 Key Findings

- Machine learning–based forecasting outperforms statistical baselines  
- Stock-out risk is highest in high-demand categories and smaller stores  
- Promotions increase demand but also increase stock-out risk  
- Demand appears relatively price inelastic within tested ranges  
- Category-specific pricing strategies outperform uniform discounting  

---

# 🧪 Demo Flow

1. Launch the Streamlit dashboard  
2. View high-level KPIs (revenue, demand, stock-out rate)  
3. Generate forecasts from input data  
4. Analyse inventory gaps and recommendations  
5. Explore pricing and promotion effects  

---

# 🚀 How to Run

### 🔹 Local Development

```bash
pip install -r requirements.txt
python -m uvicorn src.api.app:app --reload --port 8000
streamlit run src/dashboard/streamlit_app.py
```

- API Docs: http://localhost:8000/docs  
- Dashboard: http://localhost:8501  

---

### 🔹 Docker (Full System)

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

---

# 🚦 Implementation Status

| Component | Status | Notes |
|---------|--------|-------|
| Repository structure | ✅ Implemented | Modular, scalable layout |
| Synthetic data generation | ✅ Implemented | Retail-like dataset |
| Exploratory Data Analysis | ✅ Implemented | EDA notebooks completed |
| Baseline forecasting | ✅ Implemented | Statistical benchmarks |
| ML forecasting (XGBoost) | ✅ Implemented | Model trained & evaluated |
| Stock-out classification | ✅ Implemented | Binary classifier |
| Pricing analysis | ⚠️ Partial | Elasticity & optimisation |
| GenAI RAG experiments | ⚠️ Experimental | Notebook-based |
| FastAPI backend | ✅ Implemented | API scaffold ready |
| Dockerisation | ✅ Implemented | API & dashboard containerised |
| AWS deployment | 🛠 Planned | Future MLOps layer |

---

# 📁 Project Structure

```text
sunnybest-ai-forecasting-intelligence/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── Makefile
│
├── docs/
│   ├── system_overview.md
│   ├── business_context.md
│   ├── data_model.md
│   ├── data_dictionary.md
│   ├── forecasting_targets.md
│   ├── methodology.md
│   ├── assumptions.md
│   ├── api_reference.md
│   ├── changelog.md
│   └── roadmap.md
│
├── data/
│   ├── raw/
│   │   ├── foundation/
│   │   │   ├── sunnybest_stores.csv
│   │   │   ├── sunnybest_products.csv
│   │   │   ├── sunnybest_calendar.csv
│   │   │   └── sunnybest_weather.csv
│   │   │
│   │   ├── transactions/
│   │   │   ├── sunnybest_sales.csv
│   │   │   ├── sunnybest_inventory.csv
│   │   │   └── sunnybest_promotions.csv
│   │   │
│   │   ├── behaviour_operations/
│   │   │   ├── sunnybest_customer_activity.csv
│   │   │   └── sunnybest_store_operations.csv
│   │   │
│   │   └── policy_constraints/
│   │       ├── sunnybest_policy_regimes.csv
│   │       └── sunnybest_restriction_events.csv
│   │
│   ├── processed/                  # gitignored
│   ├── external/
│   └── knowledge/                  # AI/RAG knowledge base
│       ├── chunks.jsonl
│       └── embeddings.npz
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_eda_system_overview.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_demand_forecasting_baseline.ipynb
│   ├── 05_ml_forecasting_xgboost.ipynb
│   ├── 06_inventory_and_stockout_analysis.ipynb
│   ├── 07_promotion_and_price_effects.ipynb
│   ├── 08_operational_workload_analysis.ipynb
│   ├── 09_policy_impact_analysis.ipynb
│   ├── 10_scenario_planning.ipynb
│   └── 11_genai_rag_experiments.ipynb
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── constraints.yaml
│   │   └── registry.yaml
│
│   ├── data/
│   │   ├── loaders.py
│   │   ├── joins.py
│   │   └── make_dataset.py
│
│   ├── validation/
│   │   ├── schema_checks.py
│   │   ├── data_quality.py
│   │   └── business_rules.py
│
│   ├── features/
│   │   ├── build_features.py
│   │   ├── demand_features.py
│   │   ├── calendar_features.py
│   │   ├── promo_features.py
│   │   ├── inventory_features.py
│   │   └── operational_features.py
│
│   ├── forecasting/
│   │   ├── train.py
│   │   ├── predict.py
│   │   ├── evaluate.py
│   │   ├── backtest.py
│   │   ├── pipelines.py
│   │   └── registry.py
│
│   ├── operations/
│   │   ├── kpis.py
│   │   ├── service_metrics.py
│   │   ├── workload_analysis.py
│   │   ├── bottlenecks.py
│   │   └── operational_risk.py
│
│   ├── inventory/
│   │   ├── stockout_model.py
│   │   ├── replenishment.py
│   │   ├── service_level.py
│   │   └── risk_scoring.py
│
│   ├── pricing/
│   │   ├── elasticity.py
│   │   ├── build_elasticity.py
│   │   └── optimizer.py
│
│   ├── policy/
│   │   ├── policy_engine.py
│   │   ├── policy_effects.py
│   │   └── constraint_application.py
│
│   ├── planning/
│   │   ├── scenario_engine.py
│   │   ├── what_if.py
│   │   ├── assumptions.py
│   │   ├── capacity_planning.py
│   │   └── plan_generation.py
│
│   ├── genai/
│   │   ├── router.py
│   │   ├── openai_client.py
│   │   ├── schemas.py
│   │   ├── assistant/
│   │   │   ├── qa_assistant.py
│   │   │   ├── forecast_explainer.py
│   │   │   └── marketing_assistant.py
│   │   ├── tools/
│   │   │   ├── forecast_tool.py
│   │   │   ├── assumptions_tool.py
│   │   │   ├── changelog_tool.py
│   │   │   └── inventory_tool.py
│   │   ├── prompts/
│   │   │   ├── system_prompt.md
│   │   │   ├── qa_prompt.md
│   │   │   ├── forecast_explainer_prompt.md
│   │   │   └── marketing_prompt.md
│   │   └── rag/
│   │       ├── ingest.py
│   │       ├── loaders.py
│   │       ├── chunking.py
│   │       ├── embeddings.py
│   │       ├── vector_store.py
│   │       ├── retrieve.py
│   │       └── context_builder.py
│
│   ├── agents/
│   │   ├── base.py
│   │   ├── pricing_agent.py
│   │   ├── promo_agent.py
│   │   ├── inventory_agent.py
│   │   └── policies.py
│
│   ├── monitoring/
│   │   ├── metrics.py
│   │   ├── drift.py
│   │   ├── rules.py
│   │   └── store.py
│
│   ├── governance/
│   │   ├── audit_log.py
│   │   ├── schemas.py
│   │   ├── fairness.py
│   │   └── explainability.py
│
│   ├── api/
│   │   ├── app.py
│   │   └── routes/
│   │       ├── predict.py
│   │       ├── agents.py
│   │       ├── monitoring.py
│   │       └── ai.py
│
│   ├── dashboard/
│   │   └── streamlit_app.py
│
│   ├── spark/
│   │   ├── spark_session.py
│   │   ├── spark_etl.py
│   │   ├── spark_aggregations.py
│   │   └── spark_feature_engineering.py
│
│   └── warehouse/
│       ├── staging.sql
│       ├── marts.sql
│       ├── queries.sql
│       └── schema.sql
│
├── models/
│   ├── demand_forecast.pkl
│   └── stockout_model.pkl
│
├── monitoring/
│   ├── predictions_log.csv
│   ├── forecast_metrics.csv
│   ├── drift_report.csv
│   ├── agent_decisions.csv
│   └── human_overrides.csv
│
├── docker/
│   ├── Dockerfile
│   └── Dockerfile.streamlit
│
├── scripts/
│   ├── run_pipeline.sh
│   └── demo.sh
│
├── infra/
│   └── terraform/
│
├── tests/
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_forecasting.py
│   ├── test_operations.py
│   ├── test_policy.py
│   ├── test_api.py
│   └── test_ai.py
│
└── assets/
    ├── architecture.png
    └── screenshots/
```

---

# 🧭 Future Enhancements

- Full API–dashboard integration  
- Automated model retraining and monitoring  
- Cloud deployment (AWS: EC2, S3, MLOps pipelines)  
- Enhanced GenAI decision-support workflows  
- Role-based dashboards and access control  

---

# 💡 Final Note

This is not a single-model project.

It is a **forecasting intelligence system** designed to bridge:

**Data → Models → Decisions**

👉 Turning analytics into **real-world business impact**
