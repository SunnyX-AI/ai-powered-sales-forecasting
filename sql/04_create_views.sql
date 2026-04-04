-- =========================================================
-- DAILY STORE SALES
-- =========================================================

CREATE OR REPLACE VIEW analytics.vw_daily_store_sales AS
SELECT
    date,
    store_id,
    SUM(units_sold) AS total_units_sold,
    SUM(revenue) AS total_revenue
FROM core.fact_sales
GROUP BY date, store_id;

-- =========================================================
-- DAILY CATEGORY SALES
-- =========================================================

CREATE OR REPLACE VIEW analytics.vw_daily_category_sales AS
SELECT
    fs.date,
    dp.category,
    SUM(fs.units_sold) AS total_units_sold,
    SUM(fs.revenue) AS total_revenue
FROM core.fact_sales fs
JOIN core.dim_products dp
    ON fs.product_id = dp.product_id
GROUP BY fs.date, dp.category;

-- =========================================================
-- SALES + STORE ATTRIBUTES
-- =========================================================

CREATE OR REPLACE VIEW analytics.vw_sales_with_store_context AS
SELECT
    fs.date,
    fs.store_id,
    ds.store_name,
    ds.city,
    ds.region,
    ds.store_type,
    ds.store_size,
    fs.product_id,
    fs.units_sold,
    fs.revenue,
    fs.promo_flag,
    fs.discount_pct,
    fs.stockout_occurred,
    fs.restriction_active
FROM core.fact_sales fs
JOIN core.dim_stores ds
    ON fs.store_id = ds.store_id;

-- =========================================================
-- SALES + PRODUCT ATTRIBUTES
-- =========================================================

CREATE OR REPLACE VIEW analytics.vw_sales_with_product_context AS
SELECT
    fs.date,
    fs.store_id,
    fs.product_id,
    dp.product_name,
    dp.category,
    dp.brand,
    dp.regular_price,
    fs.price,
    fs.discount_pct,
    fs.units_sold,
    fs.revenue
FROM core.fact_sales fs
JOIN core.dim_products dp
    ON fs.product_id = dp.product_id;

-- =========================================================
-- SALES + WEATHER
-- =========================================================

CREATE OR REPLACE VIEW analytics.vw_sales_with_weather AS
SELECT
    fs.date,
    fs.store_id,
    ds.city,
    fs.product_id,
    fs.units_sold,
    fs.revenue,
    fw.temperature_c,
    fw.rainfall_mm,
    fw.weather_condition
FROM core.fact_sales fs
JOIN core.dim_stores ds
    ON fs.store_id = ds.store_id
LEFT JOIN core.fact_weather fw
    ON fs.date = fw.date
   AND ds.city = fw.city;

-- =========================================================
-- SALES + PROMOTIONS
-- =========================================================

CREATE OR REPLACE VIEW analytics.vw_sales_with_promotions AS
SELECT
    fs.date,
    fs.store_id,
    fs.product_id,
    fs.units_sold,
    fs.revenue,
    fp.promo_type,
    fp.discount_pct,
    fp.promo_flag
FROM core.fact_sales fs
LEFT JOIN core.fact_promotions fp
    ON fs.date = fp.date
   AND fs.store_id = fp.store_id
   AND fs.product_id = fp.product_id;

-- =========================================================
-- FORECASTING DATASET VIEW
-- =========================================================

CREATE OR REPLACE VIEW analytics.vw_forecast_dataset AS
SELECT
    fs.date,
    fs.store_id,
    ds.city,
    ds.region,
    ds.store_type,
    ds.store_size,
    fs.product_id,
    dp.product_name,
    dp.category,
    dp.brand,
    fs.units_sold,
    fs.price,
    fs.regular_price,
    fs.discount_pct,
    fs.promo_flag,
    fs.promo_type,
    fs.revenue,
    fs.starting_inventory,
    fs.restock_qty,
    fs.ending_inventory,
    fs.stockout_occurred,
    fs.restriction_active,
    fs.restriction_type,
    dc.year,
    dc.month,
    dc.day,
    dc.day_of_week,
    dc.week_of_year,
    dc.is_weekend,
    dc.is_holiday,
    dc.is_payday,
    dc.season,
    dc.is_black_friday_period,
    fw.temperature_c,
    fw.rainfall_mm,
    fw.weather_condition
FROM core.fact_sales fs
JOIN core.dim_stores ds
    ON fs.store_id = ds.store_id
JOIN core.dim_products dp
    ON fs.product_id = dp.product_id
JOIN core.dim_calendar dc
    ON fs.date = dc.date
LEFT JOIN core.fact_weather fw
    ON fs.date = fw.date
   AND ds.city = fw.city;