#!/usr/bin/env python3
"""
Check cadet table schema
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
    """Check cadet table schema"""
    conn = get_database_connection()
    cursor = conn.cursor()

    # Get cadet table columns
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'cadet'
        ORDER BY ordinal_position
    """)

    columns = cursor.fetchall()

    print("PostgreSQL Cadet table columns:")
    for column in columns:
        print(f"  {column[0]} - {column[1]} - nullable: {column[2]}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
