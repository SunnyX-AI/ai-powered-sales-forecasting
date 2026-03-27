import psycopg2
import pandas as pd


def get_connection():
    conn = psycopg2.connect(
        dbname="sunnybest_sfs",
        user="bonaventure",
        host="localhost",
        port="5432"
    )
    return conn


def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()