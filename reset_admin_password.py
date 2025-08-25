#!/usr/bin/env python3
"""Reset admin user password"""

import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

def get_database_connection():
    """Get database connection using DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not found")
        return None

    # Convert postgres:// to postgresql:// for psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def reset_admin_password():
    """Reset admin user password to a simple known password"""
    conn = get_database_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # New password: admin123
        new_password = "admin123"
        password_hash = generate_password_hash(new_password, method='scrypt')

        # Update admin user password
        cursor.execute("""
            UPDATE "user"
            SET password_hash = %s,
                password_changed_at = NOW(),
                force_password_change = false
            WHERE username = 'admin'
        """, (password_hash,))

        if cursor.rowcount == 0:
            print("❌ Admin user not found in database")
            return False

        conn.commit()
        print("✅ Admin password reset successfully!")
        print("🔑 New login credentials:")
        print("  • Username: admin")
        print("  • Password: admin123")
        print("  • Email: admin@afrotc695.com")

        return True

    except Exception as e:
        print(f"❌ Error resetting admin password: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = reset_admin_password()
    if success:
        print("\n🎉 You can now login with the new password!")
    else:
        print("\n💥 Failed to reset admin password!")
