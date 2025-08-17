#!/usr/bin/env python3
"""
Check the schema of the recruitment_document table
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
    """Check recruitment_document table schema"""
    print("=== Recruitment Document Table Schema ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Get table schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'recruitment_document'
            ORDER BY ordinal_position
        """)

        columns = cursor.fetchall()
        print(f"Recruitment document table has {len(columns)} columns:")

        for column in columns:
            column_name, data_type, is_nullable, column_default = column
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default = f" DEFAULT {column_default}" if column_default else ""
            print(f"  {column_name}: {data_type} {nullable}{default}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    main()
