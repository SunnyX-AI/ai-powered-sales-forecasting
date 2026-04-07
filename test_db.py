# # from src.data.db_connection import run_query

# # query = """
# # SELECT *
# # FROM core.fact_sales
# # LIMIT 5;
# # """

# # df = run_query(query)
# # print(df)

# from src.data.db_connection import run_query

# query = """
# SELECT *
# FROM analytics.vw_daily_store_sales
# LIMIT 5;
# """

# df = run_query(query)
# print(df)
# import pandas as pd
# from sqlalchemy import create_engine
 
# engine = create_engine("postgresql://sfs_reader:Chinenyennabude123@db.ogkdfmkybqtrsglcizzt.supabase.co:5432/postgres")
 
# df = pd.read_sql("SELECT * FROM core.fact_sales LIMIT 200", engine)

from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(
    "postgresql://sfs_user:Chinenyennabude123@aws-0-eu-west-2.pooler.supabase.com:6543/postgres"
)

df = pd.read_sql("SELECT * FROM core.fact_sales LIMIT 5", engine)
print(df.head())