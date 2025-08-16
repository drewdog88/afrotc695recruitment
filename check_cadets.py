#!/usr/bin/env python3
"""
Check cadet data and identify potential issues
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
    """Check cadet data"""
    print("=== Cadet Data Check ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    # Check total cadets
    cursor.execute('SELECT COUNT(*) FROM cadet')
    total_cadets = cursor.fetchone()[0]
    print(f"Total cadets: {total_cadets}")

    # Check active cadets
    cursor.execute("SELECT COUNT(*) FROM cadet WHERE status = 'active'")
    active_cadets = cursor.fetchone()[0]
    print(f"Active cadets: {active_cadets}")

    # Check cadet status distribution
    cursor.execute("SELECT status, COUNT(*) FROM cadet GROUP BY status")
    status_counts = cursor.fetchall()
    print("\nCadet status distribution:")
    for status, count in status_counts:
        print(f"  {status}: {count}")

    # Check for any cadets with missing required fields
    cursor.execute("""
        SELECT id, first_name, last_name, email, status
        FROM cadet
        WHERE first_name IS NULL OR last_name IS NULL OR email IS NULL OR status IS NULL
    """)
    problematic_cadets = cursor.fetchall()

    if problematic_cadets:
        print("\n⚠ Cadets with missing required fields:")
        for cadet in problematic_cadets:
            print(f"  ID {cadet[0]}: {cadet[1]} {cadet[2]} - {cadet[3]} - Status: {cadet[4]}")
    else:
        print("\n✓ All cadets have required fields")

    # Check for any data type issues
    try:
        cursor.execute("SELECT id, first_name, last_name, email, status FROM cadet LIMIT 5")
        sample_cadets = cursor.fetchall()
        print("\nSample cadet data:")
        for cadet in sample_cadets:
            print(f"  ID {cadet[0]}: {cadet[1]} {cadet[2]} - {cadet[3]} - Status: {cadet[4]}")
    except Exception as e:
        print(f"\n❌ Error reading cadet data: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
