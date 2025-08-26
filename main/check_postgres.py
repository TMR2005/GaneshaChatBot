import psycopg2

conn = psycopg2.connect(
    dbname="yourdbname",
    user="postgres",
    password="yourpassword",
    host="localhost",
    port="5432"
)

print("✅ Connected to PostgreSQL!")
conn.close()
