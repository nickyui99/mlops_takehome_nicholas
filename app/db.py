# /app/db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "mlops"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_db_connection()
    with conn.cursor() as cur:
        with open(os.path.join(os.path.dirname(__file__), "../sql/schema.sql")) as f:
            cur.execute(f.read())
        conn.commit()
    conn.close()
    print("✅ Database initialized")