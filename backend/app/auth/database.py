
from app.database.connection import get_connection


def create_users_table():
    """Create the authentication users table if it does not exist."""
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS app_users (
                    id BIGSERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(150) NOT NULL,
                    password_hash TEXT NOT NULL,
                    role VARCHAR(30) NOT NULL DEFAULT 'plant_user',
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        conn.commit()
    finally:
        conn.close()
