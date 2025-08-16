#!/usr/bin/env python3
"""
Script to restore all 13 high school contacts from the parse_contacts.py data
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

# Import the contact parsing function
from parse_contacts import parse_contact_data

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

def restore_all_contacts(conn):
    """Restore all 13 high school contacts"""
    cursor = conn.cursor()

    # Clear existing contacts
    cursor.execute("DELETE FROM university_contact")
    print("✓ Cleared existing contacts")

    # Get contact data from parse_contacts.py
    contacts_data = parse_contact_data()

    print(f"\nRestoring {len(contacts_data)} contacts...")

    for i, contact in enumerate(contacts_data, 1):
        try:
            # Prepare contact data for insertion
            contact_data = {
                'id': i,  # Use sequential IDs
                'university_name': contact['university_name'],
                'contact_name': contact['contact_name'],
                'contact_title': contact['contact_title'],
                'email': contact['email'],
                'phone': contact['phone'],
                'address': contact['address'],
                'notes': contact['notes'],
                'is_active': True,
                'created_at': datetime.now(),
                'last_modified': datetime.now()
            }

            cursor.execute("""
                INSERT INTO university_contact (
                    id, university_name, contact_name, contact_title, email, phone,
                    address, notes, is_active, created_at, last_modified
                ) VALUES (
                    %(id)s, %(university_name)s, %(contact_name)s, %(contact_title)s, %(email)s, %(phone)s,
                    %(address)s, %(notes)s, %(is_active)s, %(created_at)s, %(last_modified)s
                )
            """, contact_data)
            print(f"✓ Restored contact {i}: {contact['contact_name']} from {contact['university_name']}")
        except Exception as e:
            print(f"⚠ Error restoring contact {i} ({contact.get('contact_name', 'unknown')}): {e}")

    conn.commit()
    cursor.close()

def main():
    """Main restoration function"""
    print("=== Complete High School Contact Restoration ===")

    # Connect to database
    conn = get_database_connection()

    # Restore all contacts
    restore_all_contacts(conn)

    conn.close()

    print(f"\n=== Contact restoration complete ===")
    print("All 13 high school contacts have been restored!")

if __name__ == "__main__":
    main()
