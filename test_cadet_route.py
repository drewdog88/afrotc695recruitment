#!/usr/bin/env python3
"""
Test cadet route functionality
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

def test_cadet_query():
    """Test the same query that the cadet route uses"""
    print("=== Testing Cadet Route Query ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Test the same query that the cadet route uses
        cursor.execute("""
            SELECT id, first_name, last_name, email, cadet_rank, major,
                   graduation_year, status, gpa, unenrollment_date,
                   created_at, last_modified
            FROM cadet
            ORDER BY created_at DESC
        """)

        cadets = cursor.fetchall()
        print(f"✓ Query successful - found {len(cadets)} cadets")

        # Check for any potential issues
        for cadet in cadets[:3]:  # Show first 3
            print(f"  ID {cadet[0]}: {cadet[1]} {cadet[2]} - {cadet[3]} - Status: {cadet[7]}")

        # Check for any NULL values that might cause issues
        cursor.execute("""
            SELECT COUNT(*) FROM cadet
            WHERE first_name IS NULL OR last_name IS NULL OR email IS NULL
        """)
        null_count = cursor.fetchone()[0]

        if null_count > 0:
            print(f"⚠ Warning: {null_count} cadets have NULL values in required fields")
        else:
            print("✓ All cadets have required fields populated")

    except Exception as e:
        print(f"❌ Error in cadet query: {e}")
        return False

    cursor.close()
    conn.close()
    return True

def test_active_cadets():
    """Test active cadets specifically"""
    print("\n=== Testing Active Cadets ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM cadet WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        print(f"✓ Active cadets: {active_count}")

        cursor.execute("""
            SELECT id, first_name, last_name, email, cadet_rank, status
            FROM cadet
            WHERE status = 'active'
            ORDER BY first_name
        """)

        active_cadets = cursor.fetchall()
        print("Active cadet list:")
        for cadet in active_cadets:
            print(f"  {cadet[1]} {cadet[2]} - {cadet[3]} - {cadet[4]}")

    except Exception as e:
        print(f"❌ Error querying active cadets: {e}")
        return False

    cursor.close()
    conn.close()
    return True

def main():
    """Main test function"""
    print("=== Cadet Route Test ===")

    # Test basic cadet query
    if not test_cadet_query():
        print("❌ Basic cadet query failed")
        return

    # Test active cadets
    if not test_active_cadets():
        print("❌ Active cadets query failed")
        return

    print("\n✅ All cadet route tests passed!")
    print("If the web page is still failing, the issue might be:")
    print("1. Template rendering issue")
    print("2. Session/authentication issue")
    print("3. JavaScript error in the browser")
    print("4. Network connectivity issue")

if __name__ == "__main__":
    main()
