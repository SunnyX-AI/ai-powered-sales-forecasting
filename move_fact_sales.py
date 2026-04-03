import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# 1. Connect to local PostgreSQL
local_conn = psycopg2.connect(
    host="localhost",
    database="sunnybest_sfs",
    user="bonaventure",
    password="",
    port=5432
)

# 2. Read local fact_sales table
df = pd.read_sql("SELECT * FROM core.fact_sales", local_conn)

print("Local data preview:")
print(df.head())

# 3. Connect to Supabase
supabase_engine = create_engine(
    "postgresql+psycopg2://postgres:BonaData2026@db.xgtnldlybnsakxwonbac.supabase.co:5432/postgres?sslmode=require"
)

# 4. Write to Supabase
df.to_sql("fact_sales", supabase_engine, if_exists="replace", index=False)

print("✅ fact_sales moved successfully!")

local_conn.close()