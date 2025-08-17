#!/usr/bin/env python3
"""
Add realistic unenrollment dates for inactive cadets for demo purposes
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from datetime import datetime, date

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

def add_demo_unenrollment_dates():
    """Add realistic unenrollment dates for inactive cadets"""
    print("=== Adding Demo Unenrollment Dates ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Get inactive cadets without unenrollment dates
        cursor.execute("""
            SELECT id, first_name, last_name, graduation_year, status, unenrollment_date
            FROM cadet
            WHERE status = 'inactive' AND unenrollment_date IS NULL
            ORDER BY graduation_year, last_name
        """)

        inactive_cadets = cursor.fetchall()
        print(f"Found {len(inactive_cadets)} inactive cadets without unenrollment dates")

        if not inactive_cadets:
            print("No inactive cadets found without unenrollment dates")
            return True

        # Define realistic unenrollment dates based on graduation year
        # These dates represent when cadets might have left the program
        unenrollment_dates = {
            2027: [
                date(2024, 9, 15),  # Early fall semester
                date(2024, 12, 10), # End of fall semester
            ],
            2028: [
                date(2024, 3, 20),  # Spring semester
                date(2024, 6, 5),   # End of spring semester
            ]
        }

        # Update each inactive cadet with a realistic unenrollment date
        date_index = 0
        for cadet in inactive_cadets:
            cadet_id, first_name, last_name, grad_year, status, unenroll_date = cadet

            if grad_year in unenrollment_dates:
                available_dates = unenrollment_dates[grad_year]
                if date_index < len(available_dates):
                    unenroll_date = available_dates[date_index]
                    date_index += 1
                else:
                    # If we run out of predefined dates, create a reasonable one
                    unenroll_date = date(2024, 6, 15)  # Mid-year
            else:
                # For other graduation years, use a reasonable date
                unenroll_date = date(2024, 6, 15)

            # Update the cadet
            cursor.execute("""
                UPDATE cadet
                SET unenrollment_date = %s, last_modified = NOW()
                WHERE id = %s
            """, (unenroll_date, cadet_id))

            print(f"✓ Updated {first_name} {last_name} (Class of {grad_year}): {unenroll_date}")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n✅ Successfully added unenrollment dates for {len(inactive_cadets)} cadets!")
        return True

    except Exception as e:
        print(f"❌ Error adding unenrollment dates: {e}")
        return False

def verify_changes():
    """Verify the changes were applied correctly"""
    print("\n=== Verification ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Check all inactive cadets
        cursor.execute("""
            SELECT id, first_name, last_name, graduation_year, status, unenrollment_date
            FROM cadet
            WHERE status = 'inactive'
            ORDER BY graduation_year, last_name
        """)

        inactive_cadets = cursor.fetchall()
        print(f"Inactive cadets: {len(inactive_cadets)}")

        for cadet in inactive_cadets:
            cadet_id, first_name, last_name, grad_year, status, unenroll_date = cadet
            print(f"  {first_name} {last_name} (Class of {grad_year}): {unenroll_date or 'No date'}")

        # Check cadet status distribution
        cursor.execute("SELECT status, COUNT(*) FROM cadet GROUP BY status")
        status_counts = cursor.fetchall()
        print("\nCadet status distribution:")
        for status, count in status_counts:
            print(f"  {status}: {count}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error verifying changes: {e}")
        return False

    return True

def main():
    """Main function"""
    print("=== Demo Unenrollment Dates Setup ===")

    if add_demo_unenrollment_dates():
        verify_changes()
        print("\n✅ Demo setup complete!")
        print("The inactive cadets now have realistic unenrollment dates for demo purposes.")
        print("This will make charts and data visualization look more complete and realistic.")
    else:
        print("\n❌ Failed to add unenrollment dates")

if __name__ == "__main__":
    main()
