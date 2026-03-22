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

```
sunnybest-ai-forecasting-intelligence/
├── docs/                # System documentation
├── data/                # Raw, processed & knowledge data
├── notebooks/           # EDA, modelling & experiments
├── src/                 # Core system code (modular)
├── models/              # Trained models
├── monitoring/          # Logs & metrics
├── docker/              # Docker configuration
├── scripts/             # Execution scripts
├── infra/               # Infrastructure (Terraform)
├── tests/               # Unit tests
└── assets/              # Images & screenshots
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
