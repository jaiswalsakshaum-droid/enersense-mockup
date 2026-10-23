
import getpass

from app.auth.database import create_users_table
from app.auth.service import create_user
from app.database.connection import get_connection


def main():
    create_users_table()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM app_users WHERE role = 'admin' LIMIT 1"
            )
            if cur.fetchone():
                print("An admin account already exists. No account created.")
                return
    finally:
        conn.close()

    email = input("Admin email: ").strip().lower()
    full_name = input("Admin full name: ").strip()
    password = getpass.getpass("Admin password (minimum 12 characters): ")
    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        print("Passwords do not match.")
        return

    try:
        user = create_user(email, full_name, password, role="admin")
        print(f"Admin account created successfully for {user[1]}.")
    except ValueError as exc:
        print(f"Could not create admin: {exc}")
    except Exception:
        print("Account creation failed. Check the database and email, then retry.")


if __name__ == "__main__":
    main()
