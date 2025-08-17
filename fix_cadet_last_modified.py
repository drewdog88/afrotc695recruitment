#!/usr/bin/env python3
"""
Fix last_modified values for cadets to prevent template errors
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

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

def fix_cadet_last_modified():
    """Fix last_modified values for cadets"""
    print("=== Fixing Cadet Last Modified Values ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Check current state
        cursor.execute("SELECT COUNT(*) FROM cadet WHERE last_modified IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"Found {null_count} cadets with NULL last_modified")

        if null_count == 0:
            print("✓ All cadets already have last_modified values")
            return True

        # Update cadets with NULL last_modified to use created_at
        cursor.execute("""
            UPDATE cadet
            SET last_modified = created_at
            WHERE last_modified IS NULL
        """)

        updated_count = cursor.rowcount
        print(f"✓ Updated {updated_count} cadets")

        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM cadet WHERE last_modified IS NULL")
        remaining_null = cursor.fetchone()[0]

        if remaining_null == 0:
            print("✓ All cadets now have last_modified values")
        else:
            print(f"⚠ Warning: {remaining_null} cadets still have NULL last_modified")

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error fixing last_modified: {e}")
        return False

def main():
    """Main function"""
    print("=== Cadet Last Modified Fix ===")

    if fix_cadet_last_modified():
        print("\n✅ Cadet last_modified values fixed!")
        print("The cadet page should now work without 500 errors.")
    else:
        print("\n❌ Failed to fix last_modified values")

if __name__ == "__main__":
    main()
