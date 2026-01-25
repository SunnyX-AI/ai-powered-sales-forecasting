import os
import requests
import streamlit as st
import pandas as pd

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="SunnyBest Analytics Platform", layout="wide")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


# -----------------------------
# Helpers
# -----------------------------
def api_get(path: str, params: dict | None = None):
    url = f"{API_BASE_URL}{path}"
    return requests.get(url, params=params, timeout=10)

def api_post(path: str, json: dict):
    url = f"{API_BASE_URL}{path}"
    return requests.post(url, json=json, timeout=20)

def safe_json(res: requests.Response) -> dict:
    try:
        return res.json()
    except Exception:
        return {"raw_text": res.text}


# -----------------------------
# Header + API Health
# -----------------------------
st.title("📊 SunnyBest Retail Intelligence Platform")

colA, colB = st.columns([2, 1])
with colA:
    st.write("Frontend (Streamlit) calling backend (FastAPI).")
with colB:
    st.caption(f"API_BASE_URL: `{API_BASE_URL}`")

# Health check
try:
    r = api_get("/health")
    if r.status_code == 200 and r.json().get("status") == "ok":
        st.success("API connected ✅")
    else:
        st.warning(f"API reachable but health not OK: {r.status_code} | {r.text}")
except Exception as e:
    st.error(f"API not reachable: {e}")
    st.stop()


# -----------------------------
# Tabs
# -----------------------------
# ✅ Added tab11: Revenue Planning (Q1 / AVW-Style)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "Overview",
    "Predict (Revenue + Stockout)",
    "Predict Example (From Data)",
    "GenAI Ask (Copilot)",
    "Pricing Elasticity",
    "Monitoring (Confidence + Alerts)",
    "Pricing Agent (Recommendations)",
    "Inventory Agent (Reorder Decisions)",
    "Decision Summary (One-Click)",
    "Decision Plan (Pricing + Inventory)",
    "Revenue Planning (Q1 / AVW-Style)"
])




# -----------------------------
# TAB 1: OVERVIEW (lightweight)
# -----------------------------
with tab1:
    st.subheader("Business Overview (API-ready)")
    st.info(
        "This tab can later call an API endpoint like /kpis or /timeseries. "
        "For now, it's just confirming my full system wiring is working."
    )

    st.markdown("""
**What this system can do now:**
- Predict revenue and stockout probability via `POST /predict`
- Run a prediction from a real historical row via `GET /predict/example`
- Answer questions via the experimental GenAI layer `POST /ask`
""")



# -----------------------------
# TAB 2: PREDICT (POST /predict)
# -----------------------------
with tab2:
    st.subheader("Revenue Forecast + Stockout Probability")
    st.caption("Calls: `POST /predict`")

    with st.form("predict_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            price = st.number_input("Price (₦)", min_value=0.0, value=250000.0, step=1000.0)
            regular_price = st.number_input("Regular Price (₦)", min_value=0.0, value=300000.0, step=1000.0)
            discount_pct = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=15.0, step=1.0)
            promo_flag = st.selectbox("Promo Flag", [0, 1], index=1)

        with c2:
            month = st.slider("Month", 1, 12, 12)
            is_weekend = st.selectbox("Is Weekend?", [0, 1], index=1)
            is_holiday = st.selectbox("Is Holiday?", [0, 1], index=0)
            is_payday = st.selectbox("Is Payday?", [0, 1], index=1)

        with c3:
            category = st.text_input("Category", value="Mobile Phones")
            store_size = st.selectbox("Store Size", ["Small", "Medium", "Large"], index=2)
            temperature_c = st.number_input("Temperature (°C)", value=29.5, step=0.1)
            rainfall_mm = st.number_input("Rainfall (mm)", value=2.0, step=0.1)
            starting_inventory = st.number_input("Starting Inventory", min_value=0, value=12, step=1)

        submitted = st.form_submit_button("Run Prediction")

    if submitted:
        payload = {
            "price": float(price),
            "regular_price": float(regular_price),
            "discount_pct": float(discount_pct),
            "promo_flag": int(promo_flag),
            "month": int(month),
            "is_weekend": int(is_weekend),
            "is_holiday": int(is_holiday),
            "is_payday": int(is_payday),
            "category": category,
            "store_size": store_size,
            "temperature_c": float(temperature_c),
            "rainfall_mm": float(rainfall_mm),
            "starting_inventory": int(starting_inventory),
        }

        st.code(payload, language="json")

        try:
            res = api_post("/predict", payload)
            if res.status_code == 200:
                out = safe_json(res)
                m1, m2, m3 = st.columns(3)
                m1.metric("Predicted Revenue (₦)", f"{out['predicted_revenue']:,.2f}")
                m2.metric("Stockout Probability", f"{out['stockout_probability']:.3f}")
                m3.metric("Stockout Risk Band", out.get("stockout_risk_band", "N/A"))
                st.success("Prediction successful ✅")
            else:
                st.error(f"API error {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")



# -----------------------------
# TAB 3: PREDICT EXAMPLE (GET /predict/example)
# -----------------------------
with tab3:
    st.subheader("Predict Using a Real Historical Row")
    st.caption("Calls: `GET /predict/example`")

    c1, c2, c3 = st.columns(3)
    with c1:
        date = st.text_input("date (YYYY-MM-DD) optional", value="")
    with c2:
        store_id = st.text_input("store_id optional", value="")
    with c3:
        product_id = st.text_input("product_id optional", value="")

    params = {}
    if date.strip():
        params["date"] = date.strip()
    if store_id.strip():
        params["store_id"] = int(store_id.strip())
    if product_id.strip():
        params["product_id"] = int(product_id.strip())

    if st.button("Run Example Prediction"):
        try:
            res = api_get("/predict/example", params=params if params else None)
            if res.status_code == 200:
                out = safe_json(res)
                st.success("Example prediction returned ✅")
                st.json(out)
            else:
                st.error(f"API error {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")



# -----------------------------
# TAB 4: GENAI ASK (POST /ask)
# -----------------------------
with tab4:
    st.subheader("GenAI Copilot (Experimental)")
    st.caption("Calls: `POST /ask`")

    query = st.text_input("Ask a question", value="Summarise stockout drivers and what SunnyBest should do.")
    attach_payload = st.checkbox("Attach the same payload used in /predict? (optional)", value=False)

    st.info("This is your early GenAI layer: RAG-like retrieval over DOCS + a router tool (run_copilot).")

    if st.button("Ask Copilot"):
        req = {"query": query}
        if attach_payload:
            req["payload"] = {
                "category": "Mobile Phones",
                "store_size": "Large",
                "month": 12,
                "promo_flag": 1,
                "discount_pct": 15,
                "starting_inventory": 12,
            }

        try:
            res = api_post("/ask", req)
            if res.status_code == 200:
                out = safe_json(res)
                st.success("Copilot response ✅")
                if isinstance(out, str):
                    st.write(out)
                else:
                    st.json(out)
            else:
                st.error(f"API error {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")



# -------------------------
# TAB 5: PRICING ELASTICITY
# -------------------------
with tab5:
    st.subheader("📈 Price Elasticity by Category")

    st.info(
        "This section shows estimated price elasticity by product category. "
        "Elasticity is computed offline and served via the API."
    )

    try:
        response = api_get("/pricing/elasticity")
        response.raise_for_status()
        data = safe_json(response).get("items", [])

        if not data:
            st.warning("Elasticity table is empty. Build the artifact first.")
        else:
            elasticity_df = pd.DataFrame(data)
            st.dataframe(elasticity_df, use_container_width=True)

    except Exception as e:
        st.error("Failed to fetch elasticity data from API")
        st.exception(e)



# -----------------------------
# TAB 6: MONITORING
# -----------------------------
with tab6:
    st.subheader("📉 Monitoring: Recent Predictions + Alerts")
    st.caption("Calls: `GET /monitoring/recent` and `GET /monitoring/alerts`")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("### Recent Predictions (latest first)")
        try:
            res = api_get("/monitoring/recent", params={"limit": 50})
            res.raise_for_status()
            items = safe_json(res).get("items", [])
            if not items:
                st.info("No logs yet. Run a few predictions first.")
            else:
                log_df = pd.DataFrame(items)
                st.dataframe(log_df, use_container_width=True)
        except Exception as e:
            st.error("Failed to load monitoring logs")
            st.exception(e)

    with col2:
        st.write("### Alerts")
        try:
            res = api_get("/monitoring/alerts", params={"limit": 200})
            res.raise_for_status()
            alerts = safe_json(res).get("alerts", [])

            if not alerts:
                st.success("No alerts ✅")
            else:
                for a in alerts:
                    t = a.get("type", "info").upper()
                    msg = a.get("message", "")
                    if t == "RISK":
                        st.error(f"**{t}**: {msg}")
                    elif t == "WARNING":
                        st.warning(f"**{t}**: {msg}")
                    else:
                        st.info(f"**{t}**: {msg}")
        except Exception as e:
            st.error("Failed to load alerts")
            st.exception(e)



# -----------------------------
# TAB 7: Pricing Agents
# -----------------------------
with tab7:
    st.subheader("🤖 Pricing Agent (Action Recommendations)")
    st.caption("Calls: `POST /agent/pricing/recommend`")

    st.info(
        "This tab is your first real 'agent' UI: it takes business context + guardrails and returns a "
        "recommended pricing action."
    )

    with st.form("pricing_agent_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            category = st.text_input("Category", value="Mobile Phones")
            store_size = st.selectbox("Store Size", ["Small", "Medium", "Large"], index=2)
            month = st.slider("Month", 1, 12, 12)

        with c2:
            current_price = st.number_input("Current Price (₦)", min_value=0.0, value=250000.0, step=1000.0)
            regular_price = st.number_input("Regular Price (₦)", min_value=0.0, value=300000.0, step=1000.0)
            discount_pct = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=15.0, step=1.0)

        with c3:
            promo_flag = st.selectbox("Promo Flag", [0, 1], index=1)
            starting_inventory = st.number_input("Starting Inventory", min_value=0, value=12, step=1)

            max_discount = st.slider("Max Discount Guardrail (%)", 0, 80, 30, step=5)
            min_margin_pct = st.slider("Min Margin Guardrail (%)", 0, 80, 15, step=5)
            max_stockout_probability = st.slider("Max Stockout Probability", 0.0, 1.0, 0.60, step=0.05)

        agent_submitted = st.form_submit_button("Run Pricing Agent")

    if agent_submitted:
        req = {
            "payload": {
                "price": float(current_price),
                "regular_price": float(regular_price),
                "discount_pct": float(discount_pct),
                "promo_flag": int(promo_flag),
                "month": int(month),

                "is_weekend": 0,
                "is_holiday": 0,
                "is_payday": 0,

                "category": category,
                "store_size": store_size,

                "temperature_c": 29.5,
                "rainfall_mm": 2.0,

                "starting_inventory": int(starting_inventory),
            },
            "objective": "revenue",
            "max_discount_pct": float(max_discount),
            "max_stockout_probability": float(max_stockout_probability),
            "min_margin_pct": float(min_margin_pct),
            "min_price_factor": 0.70,
            "max_price_factor": 1.30,
            "n_grid": 25,
        }

        st.code(req, language="json")

        try:
            res = api_post("/agent/pricing/recommend", req)

            if res.status_code != 200:
                st.error(f"Agent API error {res.status_code}: {res.text}")
            else:
                out = safe_json(res)
                st.success("Pricing Agent recommendation returned ✅")

                rec = out.get("recommendation", {})

                rec_price = rec.get("recommended_price")
                rec_disc = rec.get("recommended_discount_pct")
                pred_rev = rec.get("predicted_revenue")
                stock_prob = rec.get("stockout_probability")

                m1, m2, m3 = st.columns(3)
                m1.metric("Recommended Price (₦)", f"{float(rec_price):,.0f}" if rec_price is not None else "N/A")
                m2.metric("Recommended Discount (%)", f"{float(rec_disc):.1f}" if rec_disc is not None else "N/A")
                m3.metric("Stockout Probability", f"{float(stock_prob):.3f}" if stock_prob is not None else "N/A")

                if pred_rev is not None:
                    st.metric("Predicted Revenue (₦)", f"{float(pred_rev):,.2f}")

                st.write("### Why")
                why = out.get("why", [])
                if why:
                    for w in why:
                        st.write(f"- {w}")
                else:
                    st.write("No explanation returned yet.")

                st.write("### Top Candidates (debug)")
                top = out.get("top_candidates", [])
                if top:
                    st.dataframe(pd.DataFrame(top), use_container_width=True)

                st.write("### Full Response")
                st.json(out)

        except Exception as e:
            st.error("Failed to call Pricing Agent endpoint")
            st.exception(e)



# -----------------------------
# TAB 8: Inventory Agent
# -----------------------------
with tab8:
    st.subheader("📦 Inventory Agent (Reorder Decisions)")
    st.caption("Calls: `POST /agent/inventory/recommend`")

    st.info(
        "This agent recommends whether to reorder now, and how much, based on forecast/stockout risk + constraints."
    )

    with st.form("inventory_agent_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            inv_category = st.text_input("Category", value="Mobile Phones", key="inv_category")
            inv_store_size = st.selectbox("Store Size", ["Small", "Medium", "Large"], index=2, key="inv_store_size")
            inv_month = st.slider("Month", 1, 12, 12, key="inv_month")

        with c2:
            inv_price = st.number_input("Price (₦)", min_value=0.0, value=250000.0, step=1000.0, key="inv_price")
            inv_regular_price = st.number_input("Regular Price (₦)", min_value=0.0, value=300000.0, step=1000.0, key="inv_regular_price")
            inv_discount_pct = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=15.0, step=1.0, key="inv_discount_pct")

        with c3:
            inv_promo_flag = st.selectbox("Promo Flag", [0, 1], index=1, key="inv_promo_flag")
            inv_starting_inventory = st.number_input("Starting Inventory", min_value=0, value=12, step=1, key="inv_starting_inventory")

            inv_lead_time_days = st.slider("Lead Time (days)", 1, 30, 7, key="inv_lead_time_days")
            inv_review_period_days = st.slider("Review Period (days)", 1, 30, 7, key="inv_review_period_days")
            inv_safety_stock_units = st.slider("Safety Stock (units)", 0, 100, 5, key="inv_safety_stock_units")
            inv_max_stockout_probability = st.slider("Max Allowed Stockout Prob", 0.0, 1.0, 0.60, step=0.05, key="inv_max_stockout_probability")

        run_inv = st.form_submit_button("Run Inventory Agent")

    if run_inv:
        req = {
            "payload": {
                "price": float(inv_price),
                "regular_price": float(inv_regular_price),
                "discount_pct": float(inv_discount_pct),
                "promo_flag": int(inv_promo_flag),
                "month": int(inv_month),

                "is_weekend": 0,
                "is_holiday": 0,
                "is_payday": 0,

                "category": inv_category,
                "store_size": inv_store_size,

                "temperature_c": 29.5,
                "rainfall_mm": 2.0,

                "starting_inventory": int(inv_starting_inventory),
            },
            "lead_time_days": int(inv_lead_time_days),
            "review_period_days": int(inv_review_period_days),
            "safety_stock_units": int(inv_safety_stock_units),
            "max_stockout_probability": float(inv_max_stockout_probability),
        }

        st.code(req, language="json")

        try:
            res = api_post("/agent/inventory/recommend", req)
            if res.status_code != 200:
                st.error(f"Agent API error {res.status_code}: {res.text}")
            else:
                out = safe_json(res)
                st.success("Inventory Agent recommendation returned ✅")

                rec = out.get("recommendation", out)

                reorder_now = rec.get("reorder_now")
                reorder_qty = rec.get("reorder_qty") or rec.get("recommended_order_qty")
                risk = rec.get("risk_band") or rec.get("stockout_risk_band")
                stock_prob = rec.get("stockout_probability")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Reorder Now?", str(reorder_now) if reorder_now is not None else "N/A")
                m2.metric("Reorder Qty", f"{int(reorder_qty)}" if reorder_qty is not None else "N/A")
                m3.metric("Risk Band", risk or "N/A")
                m4.metric("Stockout Prob", f"{float(stock_prob):.3f}" if stock_prob is not None else "N/A")

                st.write("### Why")
                why = out.get("why", [])
                if isinstance(why, list) and why:
                    for w in why:
                        st.write(f"- {w}")
                elif isinstance(why, str) and why:
                    st.write(why)
                else:
                    st.write("No explanation returned yet (add `why` in inventory_agent.py).")

                st.write("### Full Response")
                st.json(out)

        except Exception as e:
            st.error("Failed to call Inventory Agent endpoint")
            st.exception(e)



# =============================
# TAB 9: DECISION SUMMARY
# =============================
with tab9:
    st.subheader("🧠 Decision Summary (One-Click)")
    st.caption("Calls: `POST /predict`, `POST /agent/pricing/recommend`, `POST /agent/inventory/recommend`")

    st.info(
        "This tab runs ONE scenario and returns a full decision pack: "
        "Forecast + Stockout Risk + Pricing recommendation + Inventory reorder recommendation."
    )

    with st.form("decision_summary_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            ds_category = st.text_input("Category", value="Mobile Phones", key="ds_category")
            ds_store_size = st.selectbox("Store Size", ["Small", "Medium", "Large"], index=2, key="ds_store_size")
            ds_month = st.slider("Month", 1, 12, 12, key="ds_month")

        with c2:
            ds_price = st.number_input("Price (₦)", min_value=0.0, value=250000.0, step=1000.0, key="ds_price")
            ds_regular_price = st.number_input("Regular Price (₦)", min_value=0.0, value=300000.0, step=1000.0, key="ds_regular_price")
            ds_discount_pct = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=15.0, step=1.0, key="ds_discount_pct")

        with c3:
            ds_promo_flag = st.selectbox("Promo Flag", [0, 1], index=1, key="ds_promo_flag")
            ds_starting_inventory = st.number_input("Starting Inventory", min_value=0, value=12, step=1, key="ds_starting_inventory")

        st.divider()
        st.write("### Guardrails (constraints)")

        g1, g2, g3 = st.columns(3)
        with g1:
            ds_max_discount = st.slider("Max Discount (%)", 0, 80, 30, step=5, key="ds_max_discount")
            ds_min_margin_pct = st.slider("Min Margin (%)", 0, 80, 15, step=5, key="ds_min_margin_pct")
        with g2:
            ds_max_stockout_probability = st.slider("Max Stockout Probability", 0.0, 1.0, 0.60, step=0.05, key="ds_max_stockout_probability")
            ds_objective = st.selectbox("Pricing Objective", ["revenue", "profit"], index=0, key="ds_objective")
        with g3:
            ds_lead_time_days = st.slider("Lead Time (days)", 1, 30, 7, key="ds_lead_time_days")
            ds_review_period_days = st.slider("Review Period (days)", 1, 30, 7, key="ds_review_period_days")
            ds_safety_stock_units = st.slider("Safety Stock (units)", 0, 100, 5, key="ds_safety_stock_units")

        run_ds = st.form_submit_button("Run Decision Summary")

    if run_ds:
        base_payload = {
            "price": float(ds_price),
            "regular_price": float(ds_regular_price),
            "discount_pct": float(ds_discount_pct),
            "promo_flag": int(ds_promo_flag),
            "month": int(ds_month),

            "is_weekend": 0,
            "is_holiday": 0,
            "is_payday": 0,

            "category": ds_category,
            "store_size": ds_store_size,

            "temperature_c": 29.5,
            "rainfall_mm": 2.0,

            "starting_inventory": int(ds_starting_inventory),
        }

        pricing_req = {
            "payload": base_payload,
            "objective": ds_objective,
            "max_discount_pct": float(ds_max_discount),
            "max_stockout_probability": float(ds_max_stockout_probability),
            "min_margin_pct": float(ds_min_margin_pct),
            "min_price_factor": 0.70,
            "max_price_factor": 1.30,
            "n_grid": 25,
        }

        inventory_req = {
            "payload": base_payload,
            "lead_time_days": int(ds_lead_time_days),
            "review_period_days": int(ds_review_period_days),
            "safety_stock_units": int(ds_safety_stock_units),
            "max_stockout_probability": float(ds_max_stockout_probability),
        }

        st.write("### Requests (debug)")
        st.code({"predict_payload": base_payload, "pricing_req": pricing_req, "inventory_req": inventory_req}, language="json")

        try:
            pred_res = api_post("/predict", base_payload)
            pred_res.raise_for_status()
            pred_out = safe_json(pred_res)

            price_res = api_post("/agent/pricing/recommend", pricing_req)
            price_res.raise_for_status()
            price_out = safe_json(price_res)

            inv_res = api_post("/agent/inventory/recommend", inventory_req)
            inv_res.raise_for_status()
            inv_out = safe_json(inv_res)

            st.success("Decision Summary generated ✅")

            predicted_revenue = pred_out.get("predicted_revenue")
            stockout_probability = pred_out.get("stockout_probability")
            stockout_risk_band = pred_out.get("stockout_risk_band")

            pricing_rec = price_out.get("recommendation", {})
            rec_price = pricing_rec.get("recommended_price")
            rec_disc = pricing_rec.get("recommended_discount_pct")
            pricing_why = price_out.get("why", [])

            inv_rec = inv_out.get("recommendation", inv_out)
            reorder_now = inv_rec.get("reorder_now")
            reorder_qty = inv_rec.get("reorder_qty") or inv_rec.get("recommended_order_qty")
            inv_why = inv_out.get("why", inv_rec.get("why", []))

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Predicted Revenue (₦)", f"{float(predicted_revenue):,.2f}" if predicted_revenue is not None else "N/A")
            m2.metric("Stockout Probability", f"{float(stockout_probability):.3f}" if stockout_probability is not None else "N/A")
            m3.metric("Risk Band", stockout_risk_band or "N/A")
            m4.metric("Reorder Now?", str(reorder_now) if reorder_now is not None else "N/A")

            st.divider()

            cA, cB = st.columns(2)
            with cA:
                st.write("## 💰 Pricing Decision")
                st.metric("Recommended Price (₦)", f"{float(rec_price):,.0f}" if rec_price is not None else "N/A")
                st.metric("Recommended Discount (%)", f"{float(rec_disc):.1f}" if rec_disc is not None else "N/A")

                st.write("### Why (Pricing)")
                if isinstance(pricing_why, list) and pricing_why:
                    for w in pricing_why:
                        st.write(f"- {w}")
                elif isinstance(pricing_why, str) and pricing_why:
                    st.write(pricing_why)
                else:
                    st.write("No explanation returned yet.")

            with cB:
                st.write("## 📦 Inventory Decision")
                st.metric("Recommended Reorder Qty", f"{int(reorder_qty)}" if reorder_qty is not None else "N/A")

                st.write("### Why (Inventory)")
                if isinstance(inv_why, list) and inv_why:
                    for w in inv_why:
                        st.write(f"- {w}")
                elif isinstance(inv_why, str) and inv_why:
                    st.write(inv_why)
                else:
                    st.write("No explanation returned yet.")

            st.divider()
            st.write("### Full Responses (debug)")
            st.json({"predict": pred_out, "pricing_agent": price_out, "inventory_agent": inv_out})

        except requests.exceptions.HTTPError as e:
            st.error("One of the API calls failed (HTTP error).")
            st.exception(e)
        except Exception as e:
            st.error("Failed to generate Decision Summary.")
            st.exception(e)



# -----------------------------
# TAB 10: Decision Plan (Orchestrator)
# -----------------------------
with tab10:
    st.subheader("🧠 Decision Plan (Pricing + Inventory)")
    st.caption("Calls: `POST /decision/plan`")

    st.info(
        "This is the orchestrator. It combines Pricing + Inventory agents into one actionable plan."
    )

    with st.form("decision_plan_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            d_category = st.text_input("Category", value="Mobile Phones", key="d_category")
            d_store_size = st.selectbox("Store Size", ["Small", "Medium", "Large"], index=2, key="d_store_size")
            d_month = st.slider("Month", 1, 12, 12, key="d_month")

        with c2:
            d_price = st.number_input("Price (₦)", min_value=0.0, value=250000.0, step=1000.0, key="d_price")
            d_regular_price = st.number_input("Regular Price (₦)", min_value=0.0, value=300000.0, step=1000.0, key="d_regular_price")
            d_discount_pct = st.number_input("Discount %", min_value=0.0, max_value=100.0, value=15.0, step=1.0, key="d_discount_pct")

        with c3:
            d_promo_flag = st.selectbox("Promo Flag", [0, 1], index=1, key="d_promo_flag")
            d_starting_inventory = st.number_input("Starting Inventory", min_value=0, value=12, step=1, key="d_starting_inventory")

        st.markdown("### Guardrails / Constraints")
        gc1, gc2, gc3 = st.columns(3)

        with gc1:
            pricing_objective = st.selectbox("Pricing Objective", ["revenue", "profit"], index=0, key="d_obj")
            max_discount_pct = st.slider("Max Discount (%)", 0, 80, 30, step=5, key="d_max_disc")
            max_stockout_pricing = st.slider("Max Stockout Prob (Pricing)", 0.0, 1.0, 0.60, step=0.05, key="d_max_stock_pr")

        with gc2:
            max_stockout_inventory = st.slider("Reorder Trigger Prob (Inventory)", 0.0, 1.0, 0.40, step=0.05, key="d_max_stock_inv")
            safety_stock_units = st.slider("Safety Stock (units)", 0, 100, 5, key="d_safety")
            max_reorder_units = st.slider("Max Reorder Units", 0, 2000, 500, step=50, key="d_max_reorder")

        with gc3:
            min_price_factor = st.slider("Min Price Factor", 0.10, 1.00, 0.70, step=0.05, key="d_min_pf")
            max_price_factor = st.slider("Max Price Factor", 1.00, 2.00, 1.30, step=0.05, key="d_max_pf")
            n_grid = st.slider("Price Search Grid (n)", 5, 60, 25, step=5, key="d_grid")

        run_plan = st.form_submit_button("Run Decision Plan")

    if run_plan:
        req = {
            "payload": {
                "price": float(d_price),
                "regular_price": float(d_regular_price),
                "discount_pct": float(d_discount_pct),
                "promo_flag": int(d_promo_flag),
                "month": int(d_month),

                "is_weekend": 0,
                "is_holiday": 0,
                "is_payday": 0,

                "category": d_category,
                "store_size": d_store_size,
                "temperature_c": 29.5,
                "rainfall_mm": 2.0,
                "starting_inventory": int(d_starting_inventory),
            },

            "pricing_objective": pricing_objective,
            "max_discount_pct": float(max_discount_pct),
            "max_stockout_probability_pricing": float(max_stockout_pricing),
            "min_margin_pct": None,
            "min_price_factor": float(min_price_factor),
            "max_price_factor": float(max_price_factor),
            "n_grid": int(n_grid),

            "max_stockout_probability_inventory": float(max_stockout_inventory),
            "safety_stock_units": int(safety_stock_units),
            "max_reorder_units": int(max_reorder_units),
        }

        st.code(req, language="json")

        try:
            res = api_post("/decision/plan", req)
            if res.status_code != 200:
                st.error(f"Decision API error {res.status_code}: {res.text}")
            else:
                out = safe_json(res)
                st.success("Decision Plan returned ✅")

                plan = out.get("plan", {})
                pricing_action = plan.get("pricing_action") or {}
                inventory_action = plan.get("inventory_action") or {}

                st.write("## ✅ Action Plan Summary")
                cA, cB, cC, cD = st.columns(4)

                cA.metric("Recommended Price", f"{pricing_action.get('recommended_price', 'N/A')}")
                cB.metric("Recommended Discount %", f"{pricing_action.get('recommended_discount_pct', 'N/A')}")
                cC.metric("Reorder Now?", str(inventory_action.get("trigger_reorder", "N/A")))
                cD.metric("Reorder Units", str(inventory_action.get("recommended_reorder_units", 'N/A')))

                notes = plan.get("notes", [])
                if notes:
                    st.warning("### Notes")
                    for n in notes:
                        st.write(f"- {n}")

                st.write("### Full Response (debug)")
                st.json(out)

        except Exception as e:
            st.error("Failed to call /decision/plan")
            st.exception(e)



# =============================
# TAB 11: REVENUE PLANNING (NEW)
# =============================
with tab11:
    st.subheader("📆 Revenue Planning (Q1 / AVW-Style)")
    st.caption("Calls: `POST /plan/revenue` (monthly totals for planning)")

    st.info(
        "This is the AVW-style planning view. "
        "You pick an anchor date (e.g., end of December), a forecast window (Jan–Mar), "
        "and scenario assumptions (promo/discount). The API returns monthly totals for planning."
    )

    with st.form("revenue_plan_form"):
        p1, p2, p3 = st.columns(3)

        with p1:
            anchor_date = st.text_input("Anchor Date (YYYY-MM-DD)", value="2024-12-31")
            history_months = st.slider("History Months (lookback)", min_value=1, max_value=24, value=6, step=1)

        with p2:
            start_date = st.text_input("Forecast Start Date (YYYY-MM-DD)", value="2025-01-01")
            end_date = st.text_input("Forecast End Date (YYYY-MM-DD)", value="2025-03-31")

        with p3:
            promo_flag = st.selectbox("Promo Flag (assumption)", [0, 1], index=0)
            discount_pct = st.number_input("Discount % (assumption)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)

        run_plan = st.form_submit_button("Run Revenue Plan")

    if run_plan:
        req = {
            "anchor_date": anchor_date,
            "start_date": start_date,
            "end_date": end_date,
            "history_months": int(history_months),
            "promo_flag": int(promo_flag),
            "discount_pct": float(discount_pct),
        }

        st.code(req, language="json")

        try:
            res = api_post("/plan/revenue", req)

            if res.status_code != 200:
                st.error(f"Planning API error {res.status_code}: {res.text}")
            else:
                out = safe_json(res)
                st.success("Revenue plan returned ✅")

                monthly = out.get("monthly_total", [])

                if not monthly:
                    st.warning("No monthly totals returned. Check API response shape.")
                    st.json(out)
                else:
                    dfm = pd.DataFrame(monthly)

                    # Try to standardize month column naming
                    # (aggregate_monthly might return 'month' or 'year_month')
                    if "year_month" in dfm.columns:
                        dfm["month"] = dfm["year_month"].astype(str)
                    elif "month" in dfm.columns and dfm["month"].dtype != object:
                        dfm["month"] = dfm["month"].astype(str)

                    st.write("### Monthly Totals (Planning)")
                    st.dataframe(dfm, use_container_width=True)

                    # Identify the total column
                    total_col = None
                    for cand in ["pred_revenue", "predicted_revenue", "revenue", "total_revenue", "monthly_revenue"]:
                        if cand in dfm.columns:
                            total_col = cand
                            break

                    if total_col is not None and "month" in dfm.columns:
                        st.write("### Trend (Monthly)")
                        chart_df = dfm[["month", total_col]].copy()
                        chart_df = chart_df.sort_values("month")
                        chart_df = chart_df.set_index("month")
                        st.line_chart(chart_df)

                    # Download option
                    csv = dfm.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Download Monthly Plan CSV",
                        data=csv,
                        file_name="sunnybest_revenue_plan_monthly.csv",
                        mime="text/csv",
                    )

                    st.write("### Full Response (debug)")
                    st.json(out)

        except Exception as e:
            st.error("Failed to call /plan/revenue")
            st.exception(e)