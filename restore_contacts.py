#!/usr/bin/env python3
"""
Script to restore contact data from backup to university_contact table
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
            # Map backup contact fields to university_contact table
            contact_data = {
                'id': contact.get('id'),
                'name': contact.get('name'),
                'title': contact.get('title'),
                'email': contact.get('email'),
                'phone': contact.get('phone'),
                'school': contact.get('organization'),  # Map 'organization' to 'school'
                'department': None,  # Not in backup, set to None
                'notes': contact.get('notes'),
                'created_at': contact.get('created_at'),
                'updated_at': contact.get('updated_at')
            }

            cursor.execute("""
                INSERT INTO university_contact (
                    id, name, title, email, phone, school, department,
                    notes, created_at, updated_at
                ) VALUES (
                    %(id)s, %(name)s, %(title)s, %(email)s, %(phone)s, %(school)s, %(department)s,
                    %(notes)s, %(created_at)s, %(updated_at)s
                ) ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    title = EXCLUDED.title,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    school = EXCLUDED.school,
                    department = EXCLUDED.department,
                    notes = EXCLUDED.notes,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
            """, contact_data)
            print(f"✓ Restored contact {contact['name']} from {contact.get('organization', 'Unknown')}")
        except Exception as e:
            print(f"⚠ Error restoring contact {contact.get('name', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def main():
    """Main restoration function"""
    print("=== Contact Data Restoration ===")

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
