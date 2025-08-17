#!/usr/bin/env python3
"""
Test the improved cadet route with safe last_modified handling
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

def test_safe_properties():
    """Test the new safe properties for last_modified handling"""
    print("=== Testing Safe Properties ===")

    # Import Flask app to test the model properties
    try:
        from app import app, db, Cadet

        with app.app_context():
            # Get a few cadets to test
            cadets = Cadet.query.limit(3).all()
            print(f"Testing {len(cadets)} cadets")

            for i, cadet in enumerate(cadets, 1):
                print(f"\nCadet {i}: {cadet.first_name} {cadet.last_name}")
                print(f"  Raw last_modified: {cadet.last_modified} (type: {type(cadet.last_modified)})")
                print(f"  Raw created_at: {cadet.created_at} (type: {type(cadet.created_at)})")
                print(f"  last_modified_display: {cadet.last_modified_display}")
                print(f"  last_modified_iso: {cadet.last_modified_iso}")

                # Test that properties don't crash
                try:
                    display = cadet.last_modified_display
                    iso = cadet.last_modified_iso
                    print(f"  ✓ Properties work correctly")
                except Exception as e:
                    print(f"  ❌ Property error: {e}")

            print("\n✓ All safe properties tested successfully!")
            return True

    except Exception as e:
        print(f"❌ Error testing safe properties: {e}")
        return False

def test_template_safety():
    """Test that all cadet data is safe for template rendering"""
    print("\n=== Testing Template Safety ===")

    try:
        from app import app, db, Cadet

        with app.app_context():
            cadets = Cadet.query.all()
            print(f"Testing {len(cadets)} cadets for template safety")

            for cadet in cadets:
                try:
                    # Test all properties that might be used in templates
                    str(cadet.first_name)
                    str(cadet.last_name)
                    str(cadet.email)
                    str(cadet.cadet_rank)
                    str(cadet.major)
                    str(cadet.status)

                    if cadet.graduation_year is not None:
                        int(cadet.graduation_year)
                    if cadet.gpa is not None:
                        float(cadet.gpa)

                    # Test the safe properties
                    cadet.unenrollment_date_display
                    cadet.last_modified_display
                    cadet.last_modified_iso

                except Exception as e:
                    print(f"❌ Template safety issue with cadet {cadet.id}: {e}")
                    return False

            print("✓ All cadets are template-safe")
            return True

    except Exception as e:
        print(f"❌ Error testing template safety: {e}")
        return False

def main():
    """Main test function"""
    print("=== Improved Cadet Route Testing ===")

    if not test_safe_properties():
        print("❌ Safe properties test failed")
        return

    if not test_template_safety():
        print("❌ Template safety test failed")
        return

    print("\n✅ All tests passed!")
    print("The cadet page should now handle NULL last_modified values gracefully.")
    print("Key improvements:")
    print("1. last_modified_display falls back to created_at if last_modified is NULL")
    print("2. last_modified_iso provides safe ISO format for data attributes")
    print("3. Template uses safe properties instead of direct field access")
    print("4. No more 500 errors from NULL datetime formatting")

if __name__ == "__main__":
    main()
