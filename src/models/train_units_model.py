import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="sunnybest_sfs",
    user="bonaventure",
    password=""
)

query = "SELECT * FROM core.fact_sales"
df = pd.read_sql(query, conn)

print(df.head())