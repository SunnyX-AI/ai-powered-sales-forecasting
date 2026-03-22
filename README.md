# 🧠 SunnyBest Forecasting System (SFS)  
## 📦 AI-Powered Demand, Inventory & Retail Intelligence Platform

An end-to-end **AI, Machine Learning, and Generative AI–driven forecasting system** built for a telecom and consumer electronics retailer.

The system transforms raw retail data into **forecast-driven inventory decisions**, enabling planners to answer:

> “How much stock should we order over the next 4–8 weeks?”

---

# 🚀 Key Capability (What Makes This Project Strong)

This system is designed around a **real business workflow**:

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

- Demand volatility and seasonality  
- Stock-outs and lost revenue  
- Promotion uncertainty  
- Pricing sensitivity  
- Limited access to insights  

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
- Datasets are joined into a modelling table  
- Features are engineered (lags, promos, weather, etc.)  
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
- Stock-out risk  
- Inventory gaps  
- Recommended stock orders  

---

# 🧠 Generative AI Layer

- RAG over system knowledge  
- Natural language queries:
  - “Why did sales drop?”  
  - “Which stores are at risk?”  
- Insight summarisation for non-technical users  

---

# 📈 Key Findings

- ML models outperform statistical baselines  
- Stock-out risk is highest in high-demand categories  
- Promotions increase demand but also stock-out risk  
- Demand is relatively price inelastic in some segments  
- Category-specific pricing outperforms uniform discounting  

---

# 🧪 Demo Flow

1. Launch dashboard  
2. Upload data / explore metrics  
3. Generate forecasts  
4. View inventory recommendations  
5. Analyse pricing & promotion impact  

---

# 🚀 How to Run

### Local

```bash
pip install -r requirements.txt
python -m uvicorn src.api.app:app --reload --port 8000
streamlit run src/dashboard/streamlit_app.py
```

- API: http://localhost:8000/docs  
- Dashboard: http://localhost:8501  

---

### Docker

```bash
docker compose up --build
```

---

# 📁 Project Structure

(unchanged — keep your current structure here)

---

# 🚦 Implementation Status

(keep your table — it's good)

---

# 🧭 Future Enhancements

- Full API-dashboard integration  
- Automated retraining pipelines  
- AWS deployment (EC2, S3)  
- Enhanced GenAI workflows  
- User-specific dashboards  

---

# 💡 Final Note

This is not a single-model project.

It is a **forecasting intelligence system** designed to bridge:

- Data → Models → Decisions  

👉 Turning analytics into **real-world business impact**
