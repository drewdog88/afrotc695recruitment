#!/usr/bin/env python3
"""
Fix user data with proper first_name and last_name
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get connection to production database"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        sys.exit(1)

    # Convert postgres:// to postgresql:// for psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def main():
    """Fix user data"""
    print("=== Fix User Data ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    # Check current user data
    cursor.execute('SELECT id, username, email, first_name, last_name FROM "user"')
    users = cursor.fetchall()

    print(f"Found {len(users)} users:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, First: {user[3]}, Last: {user[4]}")

    # Fix admin user
    cursor.execute("""
        UPDATE "user"
        SET first_name = 'Admin', last_name = 'User'
        WHERE username = 'admin'
    """)

    if cursor.rowcount > 0:
        print("✓ Fixed admin user first_name and last_name")
    else:
        print("⚠ No admin user found to fix")

    conn.commit()
    cursor.close()
    conn.close()

    print("=== User data fix complete ===")

if __name__ == "__main__":
    main()
