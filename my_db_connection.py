import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

host = "YOUR_HOST"
port = 5432
database = "postgres"
user = "postgres"
password = quote_plus("YOUR_PASSWORD")

engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
    pool_pre_ping=True
)

df = pd.read_sql("SELECT * FROM core.fact_customer_activity LIMIT 5", engine)
print(df.head())