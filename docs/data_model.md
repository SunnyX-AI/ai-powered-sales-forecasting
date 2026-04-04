# SunnyBest Forecasting System (SFS) – Data Model

This document defines the structural data model of the SunnyBest Forecasting System (SFS), including table relationships, keys, and how datasets are combined to support forecasting and analytics.

---

## 1. Core Modelling Concept

The system is built around a central analytical grain:

> **date × store_id × product_id**

This represents the fundamental unit of demand and is the basis for forecasting and analysis.

---

## 2. Data Layers

The system follows a layered data architecture:

1. **Foundation Layer** – static reference data  
2. **Transaction Layer** – core business activity  
3. **Behaviour & Operations Layer** – demand drivers  
4. **Policy Layer** – constraints and external rules  

---

## 3. Primary Keys and Foreign Keys

### Primary Keys

| Table | Primary Key |
|------|------------|
| sunnybest_stores | store_id |
| sunnybest_products | product_id |
| sunnybest_calendar | date |
| sunnybest_weather | date + city |
| sunnybest_sales | date + store_id + product_id |
| sunnybest_inventory | date + store_id + product_id |
| sunnybest_promotions | date + store_id + product_id |
| sunnybest_customer_activity | date + store_id |
| sunnybest_store_operations | date + store_id |

---

### Foreign Key Relationships

| From Table | Column | To Table | Column |
|----------|--------|----------|--------|
| sales | store_id | stores | store_id |
| sales | product_id | products | product_id |
| sales | date | calendar | date |
| inventory | store_id | stores | store_id |
| inventory | product_id | products | product_id |
| promotions | store_id | stores | store_id |
| promotions | product_id | products | product_id |
| customer_activity | store_id | stores | store_id |
| store_operations | store_id | stores | store_id |
| weather | city | stores | city |

---

## 4. Star Schema Design

The system follows a **fact + dimensions structure**:

### Fact Table
- `sunnybest_sales` → central fact table

### Dimension Tables
- Stores
- Products
- Calendar
- Weather

### Supporting Fact Tables
- Inventory
- Promotions
- Customer activity
- Store operations

---

## 5. Canonical Modelling Dataset

The forecasting dataset is built by joining multiple sources:

### Base Table
- `sunnybest_sales`

### Enrichments

Joined using:

```text
sales
+ stores (store_id)
+ products (product_id)
+ calendar (date)
+ weather (date + city)
+ promotions (date + store_id + product_id)
+ inventory (date + store_id + product_id)
+ customer_activity (date + store_id)
+ store_operations (date + store_id)