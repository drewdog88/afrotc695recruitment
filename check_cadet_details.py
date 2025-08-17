#!/usr/bin/env python3
"""
Get detailed cadet information for demo planning
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
    """Get detailed cadet information"""
    print("=== Detailed Cadet Information ===")
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Get all cadets with detailed information
        cursor.execute("""
            SELECT id, first_name, last_name, email, graduation_year, status,
                   unenrollment_date, created_at, last_modified
            FROM cadet
            ORDER BY graduation_year, status, last_name
        """)

        cadets = cursor.fetchall()
        print(f"Total cadets: {len(cadets)}")

        # Group by graduation year
        by_year = {}
        for cadet in cadets:
            year = cadet[4]  # graduation_year
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(cadet)

        print("\n=== Cadets by Graduation Year ===")
        for year in sorted(by_year.keys()):
            print(f"\nGraduation Year {year}:")
            for cadet in by_year[year]:
                cadet_id, first_name, last_name, email, grad_year, status, unenroll_date, created_at, last_modified = cadet
                print(f"  ID {cadet_id}: {first_name} {last_name} - {email}")
                print(f"    Status: {status}")
                print(f"    Unenrollment Date: {unenroll_date or 'None'}")
                print(f"    Created: {created_at}")

        # Show inactive cadets specifically
        print("\n=== Inactive Cadets (Potential for Unenrollment Dates) ===")
        inactive_cadets = [c for c in cadets if c[5] == 'inactive']
        for cadet in inactive_cadets:
            cadet_id, first_name, last_name, email, grad_year, status, unenroll_date, created_at, last_modified = cadet
            print(f"  ID {cadet_id}: {first_name} {last_name} - {email}")
            print(f"    Graduation Year: {grad_year}")
            print(f"    Unenrollment Date: {unenroll_date or 'None'}")
            print(f"    Created: {created_at}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error getting cadet details: {e}")
        return False

    return True

if __name__ == "__main__":
    main()
