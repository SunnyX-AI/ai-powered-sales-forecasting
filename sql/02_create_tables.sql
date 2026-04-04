-- =========================================================
-- CORE DIMENSION TABLES
-- =========================================================

CREATE TABLE IF NOT EXISTS core.dim_stores (
    store_id TEXT PRIMARY KEY,
    store_name TEXT,
    city TEXT,
    area TEXT,
    region TEXT,
    store_type TEXT,
    store_size TEXT
);

CREATE TABLE IF NOT EXISTS core.dim_products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    brand TEXT,
    regular_price NUMERIC,
    cost_price NUMERIC,
    is_seasonal INTEGER,
    warranty_months INTEGER
);

CREATE TABLE IF NOT EXISTS core.dim_calendar (
    date DATE PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_week TEXT,
    day_of_week_num INTEGER,
    week_of_year INTEGER,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    is_payday BOOLEAN,
    season TEXT,
    is_black_friday_period BOOLEAN
);

CREATE TABLE IF NOT EXISTS core.dim_policy_regimes (
    policy_id INTEGER PRIMARY KEY,
    policy_name TEXT,
    start_date DATE,
    end_date DATE,
    affected_category TEXT,
    affected_store_type TEXT,
    demand_multiplier NUMERIC,
    discount_cap_pct NUMERIC,
    replenishment_multiplier NUMERIC,
    service_intensity_multiplier NUMERIC
);

-- =========================================================
-- RAW TABLES
-- =========================================================

CREATE TABLE IF NOT EXISTS raw.sales_raw (
    date DATE,
    store_id TEXT,
    product_id INTEGER,
    units_sold INTEGER,
    price NUMERIC,
    regular_price NUMERIC,
    discount_pct NUMERIC,
    promo_flag INTEGER,
    promo_type TEXT,
    revenue NUMERIC,
    starting_inventory INTEGER,
    restock_qty INTEGER,
    ending_inventory INTEGER,
    stockout_occurred INTEGER,
    restriction_active INTEGER,
    restriction_type TEXT,
    city TEXT,
    store_size TEXT,
    store_type TEXT,
    category TEXT
);

-- =========================================================
-- CORE FACT TABLES
-- =========================================================

CREATE TABLE IF NOT EXISTS core.fact_sales (
    date DATE REFERENCES core.dim_calendar(date),
    store_id TEXT REFERENCES core.dim_stores(store_id),
    product_id INTEGER REFERENCES core.dim_products(product_id),
    units_sold INTEGER,
    price NUMERIC,
    regular_price NUMERIC,
    discount_pct NUMERIC,
    promo_flag INTEGER,
    promo_type TEXT,
    revenue NUMERIC,
    starting_inventory INTEGER,
    restock_qty INTEGER,
    ending_inventory INTEGER,
    stockout_occurred INTEGER,
    restriction_active INTEGER,
    restriction_type TEXT,
    PRIMARY KEY (date, store_id, product_id)
);

CREATE TABLE IF NOT EXISTS core.fact_inventory (
    date DATE REFERENCES core.dim_calendar(date),
    store_id TEXT REFERENCES core.dim_stores(store_id),
    product_id INTEGER REFERENCES core.dim_products(product_id),
    starting_inventory INTEGER,
    restock_qty INTEGER,
    ending_inventory INTEGER,
    stockout_occurred INTEGER,
    PRIMARY KEY (date, store_id, product_id)
);

CREATE TABLE IF NOT EXISTS core.fact_promotions (
    date DATE REFERENCES core.dim_calendar(date),
    store_id TEXT REFERENCES core.dim_stores(store_id),
    product_id INTEGER REFERENCES core.dim_products(product_id),
    promo_type TEXT,
    discount_pct NUMERIC,
    promo_flag INTEGER,
    PRIMARY KEY (date, store_id, product_id)
);

CREATE TABLE IF NOT EXISTS core.fact_weather (
    date DATE REFERENCES core.dim_calendar(date),
    city TEXT,
    temperature_c NUMERIC,
    rainfall_mm NUMERIC,
    weather_condition TEXT,
    PRIMARY KEY (date, city)
);

CREATE TABLE IF NOT EXISTS core.fact_store_operations (
    date DATE REFERENCES core.dim_calendar(date),
    store_id TEXT REFERENCES core.dim_stores(store_id),
    staff_on_duty INTEGER,
    customer_visits INTEGER,
    support_requests INTEGER,
    completed_interactions INTEGER,
    missed_interactions INTEGER,
    service_pressure_score NUMERIC,
    PRIMARY KEY (date, store_id)
);

CREATE TABLE IF NOT EXISTS core.fact_restriction_events (
    date DATE REFERENCES core.dim_calendar(date),
    store_id TEXT REFERENCES core.dim_stores(store_id),
    product_id INTEGER REFERENCES core.dim_products(product_id),
    restriction_type TEXT,
    restriction_reason TEXT,
    restriction_severity TEXT,
    duration_days INTEGER,
    active_flag INTEGER,
    PRIMARY KEY (date, store_id, product_id, restriction_type)
);

CREATE TABLE IF NOT EXISTS core.fact_customer_activity (
    date DATE REFERENCES core.dim_calendar(date),
    store_id TEXT REFERENCES core.dim_stores(store_id),
    active_customers INTEGER,
    new_customers INTEGER,
    returning_customers INTEGER,
    churn_risk_customers INTEGER,
    net_customer_change INTEGER,
    estimated_conversion_rate NUMERIC,
    daily_revenue NUMERIC,
    PRIMARY KEY (date, store_id)
);