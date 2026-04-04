-- =========================================================
-- 1. DAILY STORE SALES IN Q1 2026
-- =========================================================

SELECT *
FROM analytics.vw_daily_store_sales
WHERE date BETWEEN '2026-01-01' AND '2026-03-31'
ORDER BY date, store_id;

-- =========================================================
-- 2. TOP STORES BY REVENUE IN Q1 2026
-- =========================================================

SELECT
    store_id,
    SUM(total_revenue) AS q1_revenue
FROM analytics.vw_daily_store_sales
WHERE date BETWEEN '2026-01-01' AND '2026-03-31'
GROUP BY store_id
ORDER BY q1_revenue DESC;

-- =========================================================
-- 3. CATEGORY PERFORMANCE IN Q1 2026
-- =========================================================

SELECT
    category,
    SUM(total_units_sold) AS total_units,
    SUM(total_revenue) AS total_revenue
FROM analytics.vw_daily_category_sales
WHERE date BETWEEN '2026-01-01' AND '2026-03-31'
GROUP BY category
ORDER BY total_revenue DESC;

-- =========================================================
-- 4. PROMOTION IMPACT
-- =========================================================

SELECT
    promo_flag,
    AVG(units_sold) AS avg_units_sold,
    AVG(revenue) AS avg_revenue
FROM analytics.vw_sales_with_promotions
GROUP BY promo_flag
ORDER BY promo_flag;

-- =========================================================
-- 5. WEATHER VS SALES
-- =========================================================

SELECT
    weather_condition,
    AVG(units_sold) AS avg_units_sold,
    AVG(revenue) AS avg_revenue
FROM analytics.vw_sales_with_weather
GROUP BY weather_condition
ORDER BY avg_revenue DESC;

-- =========================================================
-- 6. STOCKOUT HOTSPOTS
-- =========================================================

SELECT
    store_id,
    COUNT(*) AS stockout_rows,
    SUM(units_sold) AS units_sold_during_stockout
FROM core.fact_sales
WHERE stockout_occurred = 1
GROUP BY store_id
ORDER BY stockout_rows DESC;

-- =========================================================
-- 7. RESTRICTION IMPACT
-- =========================================================

SELECT
    restriction_type,
    COUNT(*) AS affected_rows,
    AVG(units_sold) AS avg_units_sold,
    AVG(revenue) AS avg_revenue
FROM core.fact_sales
WHERE restriction_active = 1
GROUP BY restriction_type
ORDER BY affected_rows DESC;

-- =========================================================
-- 8. STORE OPERATIONS PRESSURE
-- =========================================================

SELECT
    store_id,
    AVG(service_pressure_score) AS avg_pressure,
    AVG(customer_visits) AS avg_customer_visits,
    AVG(missed_interactions) AS avg_missed_interactions
FROM core.fact_store_operations
GROUP BY store_id
ORDER BY avg_pressure DESC;

-- =========================================================
-- 9. CUSTOMER ACTIVITY SUMMARY
-- =========================================================

SELECT
    store_id,
    AVG(active_customers) AS avg_active_customers,
    AVG(new_customers) AS avg_new_customers,
    AVG(returning_customers) AS avg_returning_customers,
    AVG(churn_risk_customers) AS avg_churn_risk_customers
FROM core.fact_customer_activity
GROUP BY store_id
ORDER BY avg_active_customers DESC;

-- =========================================================
-- 10. FORECAST DATA SAMPLE
-- =========================================================

SELECT *
FROM analytics.vw_forecast_dataset
WHERE date BETWEEN '2026-01-01' AND '2026-03-31'
LIMIT 100;