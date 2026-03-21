# SunnyBest Forecasting System (SFS) – Data Overview

This document provides a detailed description of all datasets in the SunnyBest Forecasting System (SFS).  
It is intended to build strong understanding of the system, relationships between datasets, and how they support forecasting and operational analysis.

---

# 🧱 1. Foundation Layer

These datasets define the **static structure** of the system.

---

## 1.1 sunnybest_stores

### Description
Contains information about all stores in the system.

### Grain
- One row per **store**

### Key Columns
- `store_id` (Primary Key)
- `store_name`
- `city`
- `area`
- `region`
- `store_type` (Mall, Plaza, High Street)
- `store_size` (Small, Medium, Large)

### Purpose
- Defines where activity happens
- Used to analyse regional and store-level performance
- Impacts demand and operations

---

## 1.2 sunnybest_products

### Description
Contains product catalog information.

### Grain
- One row per **product**

### Key Columns
- `product_id` (Primary Key)
- `product_name`
- `category`
- `brand`
- `regular_price`
- `cost_price`
- `is_seasonal`
- `warranty_months`

### Purpose
- Defines what is being sold
- Drives demand patterns and pricing behaviour

---

## 1.3 sunnybest_calendar

### Description
Provides time-based features.

### Grain
- One row per **date**

### Key Columns
- `date`
- `year`, `month`, `day`
- `day_of_week`
- `is_weekend`
- `is_holiday`
- `is_payday`
- `season`

### Purpose
- Enables time-series modelling
- Captures seasonality and event effects

---

## 1.4 sunnybest_weather

### Description
Simulated weather data per city and date.

### Grain
- One row per **date × city**

### Key Columns
- `date`
- `city`
- `temperature_c`
- `rainfall_mm`
- `weather_condition`

### Purpose
- External driver of demand
- Affects specific categories (e.g., AC sales in heat)

---

# 📈 2. Transaction Layer

These datasets represent **core business activity**.

---

## 2.1 sunnybest_sales

### Description
Main transactional dataset containing sales activity.

### Grain
- One row per **date × store × product**

### Key Columns
- `date`, `store_id`, `product_id`
- `units_sold`
- `price`, `regular_price`, `discount_pct`
- `promo_flag`, `promo_type`
- `revenue`
- `starting_inventory`, `ending_inventory`
- `stockout_occurred`
- `restriction_active`, `restriction_type`
- `category`, `store_size`, `store_type`

### Purpose
- Core dataset for forecasting
- Captures demand, pricing, and constraints

---

## 2.2 sunnybest_inventory

### Description
Tracks inventory movement and stock levels.

### Grain
- One row per **date × store × product**

### Key Columns
- `date`, `store_id`, `product_id`
- `starting_inventory`
- `restock_qty`
- `ending_inventory`
- `stockout_flag`

### Purpose
- Enables stock analysis
- Supports inventory optimization and stockout detection

---

## 2.3 sunnybest_promotions

### Description
Contains promotion events.

### Grain
- One row per **date × store × product (when promotion exists)**

### Key Columns
- `date`, `store_id`, `product_id`
- `promo_type`
- `discount_pct`
- `promo_flag`

### Purpose
- Captures marketing actions
- Used to analyse uplift and price elasticity

---

# 🧠 3. Behaviour & Operations Layer

These datasets simulate **customer behaviour and operational workload**.

---

## 3.1 sunnybest_customer_activity

### Description
Represents customer-level behaviour at store level.

### Grain
- One row per **date × store**

### Key Columns
- `date`, `store_id`
- `active_customers`
- `new_customers`
- `returning_customers`
- `churn_risk_customers`
- `net_customer_change`
- `estimated_conversion_rate`
- `daily_revenue`

### Purpose
- Equivalent to **caseload and inflows (UC analogy)**
- Helps understand demand drivers beyond sales
- Supports customer behaviour modelling

---

## 3.2 sunnybest_store_operations

### Description
Captures operational workload and service capacity.

### Grain
- One row per **date × store**

### Key Columns
- `date`, `store_id`
- `staff_on_duty`
- `customer_visits`
- `support_requests`
- `completed_interactions`
- `missed_interactions`
- `service_pressure_score`

### Purpose
- Equivalent to **appointments and workload (UC analogy)**
- Measures operational strain
- Enables service optimisation analysis

---

# ⚖️ 4. Policy & Constraints Layer

These datasets represent **rules and restrictions affecting the system**.

---

## 4.1 sunnybest_policy_regimes

### Description
Defines business policies active over time.

### Grain
- One row per **policy regime**

### Key Columns
- `policy_id`
- `policy_name`
- `start_date`, `end_date`
- `affected_category`
- `affected_store_type`
- `demand_multiplier`
- `discount_cap_pct`
- `replenishment_multiplier`
- `service_intensity_multiplier`

### Purpose
- Represents **policy changes over time**
- Influences demand, pricing, replenishment, and operations

---

## 4.2 sunnybest_restriction_events

### Description
Represents temporary constraints affecting operations or supply.

### Grain
- One row per **restriction event**

### Key Columns
- `date`, `store_id`, `product_id`
- `restriction_type`
- `restriction_reason`
- `restriction_severity`
- `duration_days`
- `active_flag`

### Purpose
- Equivalent to **sanctions or disruptions (UC analogy)**
- Captures supply issues and operational constraints
- Impacts demand and inventory

---

# 🔗 Relationships Between Datasets

- `store_id` → links stores across all datasets
- `product_id` → links product-related datasets
- `date` → central time key across all datasets
- `city` → links weather to stores

---

# 🧠 Key Concept

The SFS is not just a dataset — it is a **multi-layer system**:

- Foundation → defines structure  
- Transactions → capture activity  
- Behaviour → explains why activity happens  
- Policies → influence system dynamics  

---

# 🎯 Summary

The SunnyBest system simulates a real-world retail ecosystem by combining:

- Sales and inventory dynamics  
- Customer behaviour  
- Operational workload  
- Policy-driven effects  

This enables:
- Forecasting  
- Scenario analysis  
- Policy impact evaluation  
- Operational optimisation  