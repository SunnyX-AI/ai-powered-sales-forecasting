# SunnyBest Forecasting System (SFS) – Data Overview

This document provides a comprehensive description of all datasets in the SunnyBest Forecasting System (SFS).  
It is designed to support a deep understanding of the system structure, dataset relationships, and how each component contributes to forecasting and operational analysis.

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
- `store_type`
- `store_size`

### Column Descriptions
- `store_id`: Unique identifier for each store  
- `store_name`: Name of the store  
- `city`: City where the store is located  
- `area`: Local administrative area within the city  
- `region`: Broader geographical region  
- `store_type`: Type of store (e.g., Mall, Plaza, High Street)  
- `store_size`: Size classification of the store (Small, Medium, Large)  

### Purpose
- Defines where business activity occurs  
- Enables geographic and store-level analysis  
- Influences demand and operational capacity  

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

### Column Descriptions
- `product_id`: Unique identifier for each product  
- `product_name`: Name of the product  
- `category`: Product category (e.g., Phones, TVs, Appliances)  
- `brand`: Brand of the product  
- `regular_price`: Standard selling price  
- `cost_price`: Purchase or production cost  
- `is_seasonal`: Indicates whether demand varies by season (1 = Yes, 0 = No)  
- `warranty_months`: Warranty duration in months  

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

### Column Descriptions
- `date`: Calendar date  
- `year`: Year component of the date  
- `month`: Month number  
- `day`: Day of the month  
- `day_of_week`: Name of the day (e.g., Monday)  
- `is_weekend`: Indicates whether the date falls on a weekend  
- `is_holiday`: Indicates whether the date is a public holiday  
- `is_payday`: Indicates typical salary payment day (e.g., 25th of month)  
- `season`: Season classification (Dry, Early Rainy, Late Rainy)  

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

### Column Descriptions
- `date`: Date of observation  
- `city`: City where weather is recorded  
- `temperature_c`: Temperature in Celsius  
- `rainfall_mm`: Rainfall in millimetres  
- `weather_condition`: Weather condition (Sunny, Cloudy, Rainy)  

### Purpose
- Acts as an external driver of demand  
- Influences weather-sensitive product categories  

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
- `category`, `store_size`, `store_type`

### Column Descriptions
- `date`: Transaction date  
- `store_id`: Store where the sale occurred  
- `product_id`: Product sold  
- `units_sold`: Number of units sold  
- `price`: Final selling price after discount  
- `regular_price`: Original price before discount  
- `discount_pct`: Percentage discount applied  
- `promo_flag`: Indicates whether a promotion was active (1 = Yes)  
- `promo_type`: Type of promotion applied  
- `revenue`: Total revenue generated (units_sold × price)  
- `starting_inventory`: Inventory available at the beginning of the day  
- `ending_inventory`: Inventory remaining after sales  
- `stockout_occurred`: Indicates whether demand exceeded available stock  
- `category`: Product category  
- `store_size`: Store size classification  
- `store_type`: Store type classification  

### Purpose
- Core dataset for forecasting  
- Captures demand, pricing, and supply constraints  

---

## 2.2 sunnybest_inventory

### Description
Tracks inventory movement and stock levels.

### Grain
- One row per **date × store × product**

### Key Columns
- `date`, `store_id`, `product_id`
- `starting_inventory`
- `ending_inventory`
- `stockout_flag`

### Column Descriptions
- `date`: Inventory record date  
- `store_id`: Store identifier  
- `product_id`: Product identifier  
- `starting_inventory`: Inventory available at start of day  
- `ending_inventory`: Inventory remaining after sales  
- `stockout_flag`: Indicates whether a stockout occurred  

### Purpose
- Enables stock monitoring and analysis  
- Supports inventory optimisation and stockout detection  

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

### Column Descriptions
- `date`: Date of promotion  
- `store_id`: Store offering the promotion  
- `product_id`: Product on promotion  
- `promo_type`: Type of promotion (e.g., Discount, Bundle)  
- `discount_pct`: Discount percentage applied  
- `promo_flag`: Indicates presence of a promotion  

### Purpose
- Captures marketing actions  
- Enables analysis of promotional uplift and price sensitivity  

---

# 🧠 3. Behaviour & Operations Layer

These datasets simulate **customer behaviour and operational workload**.

---

## 3.1 sunnybest_customer_activity

### Description
Represents customer behaviour at the store level.

### Grain
- One row per **date × store**

### Key Columns
- `date`, `store_id`
- `active_customers`
- `new_customers`
- `returning_customers`
- `churn_risk_customers`
- `estimated_conversion_rate`
- `daily_revenue`

### Column Descriptions
- `date`: Activity date  
- `store_id`: Store identifier  
- `active_customers`: Total customers visiting the store  
- `new_customers`: First-time customers  
- `returning_customers`: Repeat customers  
- `churn_risk_customers`: Customers at risk of disengaging  
- `estimated_conversion_rate`: Ratio of purchases to visits  
- `daily_revenue`: Total revenue generated per store  

### Purpose
- Represents demand drivers  
- Equivalent to **caseload and inflows (UC analogy)**  
- Supports behavioural analysis  

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

### Column Descriptions
- `date`: Operation date  
- `store_id`: Store identifier  
- `staff_on_duty`: Number of staff working  
- `customer_visits`: Number of customers visiting  
- `support_requests`: Customer service requests  
- `completed_interactions`: Successfully handled interactions  
- `missed_interactions`: Unattended customer requests  
- `service_pressure_score`: Measure of workload intensity  

### Purpose
- Represents service capacity and workload  
- Equivalent to **appointments/workload (UC analogy)**  
- Supports operational efficiency analysis  

---

# ⚖️ 4. Policy & Constraints Layer

These datasets represent **rules and constraints affecting the system**.

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

### Column Descriptions
- `policy_id`: Unique identifier for the policy  
- `policy_name`: Name of the policy  
- `start_date`: Date the policy becomes active  
- `end_date`: Date the policy ends  
- `affected_category`: Product category affected by the policy  
- `affected_store_type`: Store type impacted  
- `demand_multiplier`: Factor applied to demand  
- `discount_cap_pct`: Maximum allowed discount percentage  
- `replenishment_multiplier`: Factor affecting inventory replenishment  
- `service_intensity_multiplier`: Factor affecting workload intensity  

### Purpose
- Represents time-based business rules  
- Influences demand, pricing, inventory, and operations  

---

## 4.2 sunnybest_restriction_events

### Description
Represents temporary constraints affecting supply or operations.

### Grain
- One row per **restriction event**

### Key Columns
- `date`, `store_id`, `product_id`
- `restriction_type`
- `restriction_reason`
- `restriction_severity`
- `duration_days`
- `active_flag`

### Column Descriptions
- `date`: Date of restriction  
- `store_id`: Store affected  
- `product_id`: Product affected  
- `restriction_type`: Type of restriction  
- `restriction_reason`: Reason for restriction  
- `restriction_severity`: Severity level (Low, Medium, High)  
- `duration_days`: Duration of the restriction  
- `active_flag`: Indicates whether the restriction is active  

### Purpose
- Represents disruptions or constraints  
- Equivalent to **sanctions (UC analogy)**  
- Impacts supply and demand  

---

# 🔗 Relationships Between Datasets

- `store_id` → links all store-related datasets  
- `product_id` → links all product-related datasets  
- `date` → central time key across datasets  
- `city` → links stores to weather  

---

# 🧠 Key Concept

The SFS is a **multi-layer system**, not just a dataset:

- Foundation → defines structure  
- Transactions → capture activity  
- Behaviour → explains demand  
- Policies → influence system behaviour  

---

# 🎯 Summary

The SunnyBest system simulates a real-world retail ecosystem by integrating:

- Sales and inventory dynamics  
- Customer behaviour  
- Operational workload  
- Policy-driven effects  

This enables:

- Demand forecasting  
- Scenario simulation  
- Policy impact analysis  
- Operational optimisation  