#!/usr/bin/env python3
"""Fix admin user restore by filtering out 2FA columns"""

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

def create_admin_user():
    """Create admin user with proper schema"""
    conn = get_database_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Check if admin user already exists
        cursor.execute('SELECT id FROM "user" WHERE username = %s', ('admin',))
        existing_user = cursor.fetchone()

        if existing_user:
            print("Admin user already exists")
            return True

        # Create admin user with current schema (no 2FA columns)
        cursor.execute("""
            INSERT INTO "user" (
                username, email, password_hash, first_name, last_name,
                phone, role, is_active, is_locked, failed_login_attempts,
                password_changed_at, password_expires_at, force_password_change,
                secret_question, secret_answer_hash, created_at, last_modified
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            'admin',
            'admin@afrotc695.com',
            'scrypt:32768:8:1$G9jjBoU1yiFWhEip$16da6888cc694ed664de1caac3d8f52ac9411476ce187dfb58f36a0b1f8f33313f1b3f4148cbe30e683ad09987271c4cb728b61fa0747f01c042a28a524077ff',
            'Admin',
            'User',
            None,
            'admin',
            True,
            False,
            0,
            '2025-08-17 01:53:23.441976',
            None,
            False,
            'What is your favorite color?',
            'scrypt:32768:8:1$vUCrwA2vtCZBn9T1$aed7ad4dc70a83dbbd5ed09678c5e1ddb1679c3e2b962f1e6084f652360a2f9d2cc6831796d3157c0d2a40b42a95782af51113248b98556928a69003c989b62a',
            '2025-08-17 01:53:23.441976',
            '2025-08-17 01:53:23.441976'
        ))

        conn.commit()
        print("✅ Admin user created successfully!")
        print("🔑 Login credentials:")
        print("  • Username: admin")
        print("  • Email: admin@afrotc695.com")
        print("  • Role: admin")

        return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = create_admin_user()
    if success:
        print("\n🎉 You should now be able to login to the system!")
    else:
        print("\n💥 Failed to create admin user!")
