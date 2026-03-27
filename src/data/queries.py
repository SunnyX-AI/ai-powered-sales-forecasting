from src.data.db_connection import run_query


def fetch_sales(limit: int = 1000):
    query = f"""
    SELECT *
    FROM core.fact_sales
    LIMIT {limit};
    """
    return run_query(query)


def fetch_sales_with_weather():
    query = """
    SELECT
        s.date,
        s.store_id,
        s.product_id,
        s.units_sold,
        s.revenue,
        w.city,
        w.temperature_c,
        w.rainfall_mm,
        w.weather_condition
    FROM core.fact_sales s
    LEFT JOIN core.dim_stores st
        ON s.store_id = st.store_id
    LEFT JOIN core.fact_weather w
        ON s.date = w.date
       AND st.city = w.city;
    """
    return run_query(query)