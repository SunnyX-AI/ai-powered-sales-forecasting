-- =========================================================
-- OPTIONAL: CLEAN RELOAD
-- =========================================================

TRUNCATE TABLE
    core.fact_customer_activity,
    core.fact_inventory,
    core.fact_promotions,
    core.fact_restriction_events,
    core.fact_sales,
    core.fact_store_operations,
    core.fact_weather,
    core.dim_policy_regimes,
    core.dim_calendar,
    core.dim_products,
    core.dim_stores,
    raw.sales_raw
CASCADE;

-- =========================================================
-- LOAD DIMENSIONS
-- =========================================================

\copy core.dim_stores FROM 'data/raw/sunnybest_stores.csv' DELIMITER ',' CSV HEADER;
\copy core.dim_products FROM 'data/raw/sunnybest_products.csv' DELIMITER ',' CSV HEADER;
\copy core.dim_calendar FROM 'data/raw/sunnybest_calendar.csv' DELIMITER ',' CSV HEADER;
\copy core.dim_policy_regimes FROM 'data/raw/sunnybest_policy_regimes.csv' DELIMITER ',' CSV HEADER;

-- =========================================================
-- LOAD FACTS WITH MATCHING STRUCTURE
-- =========================================================

\copy core.fact_inventory FROM 'data/raw/sunnybest_inventory.csv' DELIMITER ',' CSV HEADER;
\copy core.fact_promotions FROM 'data/raw/sunnybest_promotions.csv' DELIMITER ',' CSV HEADER;
\copy core.fact_weather FROM 'data/raw/sunnybest_weather.csv' DELIMITER ',' CSV HEADER;
\copy core.fact_store_operations FROM 'data/raw/sunnybest_store_operations.csv' DELIMITER ',' CSV HEADER;
\copy core.fact_restriction_events FROM 'data/raw/sunnybest_restriction_events.csv' DELIMITER ',' CSV HEADER;
\copy core.fact_customer_activity FROM 'data/raw/sunnybest_customer_activity.csv' DELIMITER ',' CSV HEADER;

-- =========================================================
-- LOAD SALES THROUGH RAW TABLE
-- =========================================================

\copy raw.sales_raw FROM 'data/raw/sunnybest_sales.csv' DELIMITER ',' CSV HEADER;

INSERT INTO core.fact_sales (
    date,
    store_id,
    product_id,
    units_sold,
    price,
    regular_price,
    discount_pct,
    promo_flag,
    promo_type,
    revenue,
    starting_inventory,
    restock_qty,
    ending_inventory,
    stockout_occurred,
    restriction_active,
    restriction_type
)
SELECT
    date,
    store_id,
    product_id,
    units_sold,
    price,
    regular_price,
    discount_pct,
    promo_flag,
    promo_type,
    revenue,
    starting_inventory,
    restock_qty,
    ending_inventory,
    stockout_occurred,
    restriction_active,
    restriction_type
FROM raw.sales_raw;