#!/usr/bin/env python3
"""
Script to restore contact data from backup to university_contact table with correct schema
"""

import os
import sys
import json
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

def load_backup_data():
    """Load the latest backup data"""
    backup_file = "backups/neon_backup_20250807_145537.json"

    if not os.path.exists(backup_file):
        print(f"Error: Backup file {backup_file} not found")
        sys.exit(1)

    try:
        with open(backup_file, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading backup data: {e}")
        sys.exit(1)

def restore_contacts(conn, contacts_data):
    """Restore contacts from backup to university_contact table"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(contacts_data)} contacts...")

    for contact in contacts_data:
        try:
            # Map backup contact fields to university_contact table schema
            contact_data = {
                'id': contact.get('id'),
                'university_name': contact.get('organization'),  # Map 'organization' to 'university_name'
                'contact_name': contact.get('name'),  # Map 'name' to 'contact_name'
                'contact_title': contact.get('title'),  # Map 'title' to 'contact_title'
                'email': contact.get('email'),
                'phone': contact.get('phone'),
                'address': contact.get('address'),  # Map 'address' to 'address'
                'notes': contact.get('notes'),
                'is_active': True,  # Set to active by default
                'created_at': contact.get('created_at'),
                'last_modified': contact.get('updated_at')  # Map 'updated_at' to 'last_modified'
            }

            cursor.execute("""
                INSERT INTO university_contact (
                    id, university_name, contact_name, contact_title, email, phone,
                    address, notes, is_active, created_at, last_modified
                ) VALUES (
                    %(id)s, %(university_name)s, %(contact_name)s, %(contact_title)s, %(email)s, %(phone)s,
                    %(address)s, %(notes)s, %(is_active)s, %(created_at)s, %(last_modified)s
                ) ON CONFLICT (id) DO UPDATE SET
                    university_name = EXCLUDED.university_name,
                    contact_name = EXCLUDED.contact_name,
                    contact_title = EXCLUDED.contact_title,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    address = EXCLUDED.address,
                    notes = EXCLUDED.notes,
                    is_active = EXCLUDED.is_active,
                    created_at = EXCLUDED.created_at,
                    last_modified = EXCLUDED.last_modified
            """, contact_data)
            print(f"✓ Restored contact {contact['name']} from {contact.get('organization', 'Unknown')}")
        except Exception as e:
            print(f"⚠ Error restoring contact {contact.get('name', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def main():
    """Main restoration function"""
    print("=== Contact Data Restoration (Fixed Schema) ===")

    # Load backup data
    print("Loading backup data...")
    backup_data = load_backup_data()

    # Connect to database
    conn = get_database_connection()

    # Get contacts data from backup
    contacts_data = backup_data.get('tables', {}).get('contact', {}).get('data', [])

    if contacts_data:
        restore_contacts(conn, contacts_data)
    else:
        print("No contact data found in backup")

    conn.close()

    print("\n=== Contact restoration complete ===")

if __name__ == "__main__":
    main()
