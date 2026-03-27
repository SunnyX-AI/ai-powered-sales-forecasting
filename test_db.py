from src.data.db_connection import run_query

query = """
SELECT *
FROM core.fact_sales
LIMIT 5;
"""

df = run_query(query)
print(df)