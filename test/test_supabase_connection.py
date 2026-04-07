import psycopg2

conn = psycopg2.connect(
    host="db.xgtnldlybnsakxwonbac.supabase.co",
    database="postgres",
    user="postgres",
    password="@naven0ture01",
    port=5432,
    sslmode="require"
)

cur = conn.cursor()
cur.execute("SELECT 1;")
print(cur.fetchone())

cur.close()
conn.close()