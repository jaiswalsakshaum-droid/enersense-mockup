
from app.auth.database import create_users_table
from app.auth.security import hash_password, verify_password
from app.database.connection import get_connection


def get_user_by_email(email: str):
    """Return a user record matching the email, or None."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, email, full_name, password_hash, role, is_active
                FROM app_users
                WHERE LOWER(email) = LOWER(%s)
                """,
                (email.strip(),),
            )
            return cur.fetchone()
    finally:
        conn.close()


def create_user(email: str, full_name: str, password: str, role: str = "plant_user"):
    """Create a user with a securely hashed password."""
    email = email.strip().lower()
    full_name = full_name.strip()

    if not email or not full_name:
        raise ValueError("Email and full name are required")
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long")
    if role not in {"admin", "plant_user"}:
        raise ValueError("Invalid role")

    password_digest = hash_password(password)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO app_users (email, full_name, password_hash, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id, email, full_name, role, is_active
                """,
                (email, full_name, password_digest, role),
            )
            user = cur.fetchone()
        conn.commit()
        return user
    finally:
        conn.close()


def authenticate_user(email: str, password: str):
    """Return the active user if the email and password are valid."""
    user = get_user_by_email(email)
    if user is None:
        return None

    user_id, user_email, full_name, password_digest, role, is_active = user

    if not is_active or not verify_password(password, password_digest):
        return None

    return {
        "id": user_id,
        "email": user_email,
        "full_name": full_name,
        "role": role,
    }
