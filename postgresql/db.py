# # db.py
# import psycopg2
# from psycopg2.extras import RealDictCursor

# DB_HOST = "172.17.0.1"  # or "db" if running in Docker
# DB_PORT = "5432"
# DB_NAME = "my_first_db"
# DB_USER = "postgres"
# DB_PASSWORD = "mypassword"

# def get_db_connection():
#     """
#     Returns a new PostgreSQL connection
#     """
#     return psycopg2.connect(
#         host=DB_HOST,
#         port=DB_PORT,
#         dbname=DB_NAME,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         cursor_factory=RealDictCursor  # Optional: returns dict instead of tuple
#     )

# # ---------- Test Connection ----------
# if __name__ == "__main__":
#     try:
#         conn = get_db_connection()
#         print("✅ Database connection successful!")
#         conn.close()
#     except Exception as e:
#         print("❌ Failed to connect to database:", e)

# db.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

DB_HOST = os.getenv("POSTGRES_HOST", "postgres-service")  # Use Docker service name
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "my_first_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

if __name__ == "__main__":
    try:
        with get_db_connection() as conn:
            print("✅ Database connection successful!")
    except Exception as e:
        print("❌ Failed to connect to database:", e)
