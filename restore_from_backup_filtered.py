#!/usr/bin/env python3
"""
Script to restore data from backup with 2FA columns filtered out
"""

import os
import sys
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from datetime import datetime

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

def find_latest_backup():
    """Find the most recent backup file"""
    backup_dir = "backups"
    backup_files = []

    if not os.path.exists(backup_dir):
        print(f"Error: Backup directory {backup_dir} not found")
        sys.exit(1)

    for file in os.listdir(backup_dir):
        if file.endswith('.json') and file.startswith('afrotc695_backup_'):
            backup_files.append(file)

    if not backup_files:
        print("Error: No backup files found")
        sys.exit(1)

    # Sort by timestamp (newest first)
    backup_files.sort(reverse=True)
    latest_backup = backup_files[0]

    print(f"Found latest backup: {latest_backup}")
    return os.path.join(backup_dir, latest_backup)

def load_backup_data(backup_file):
    """Load the backup data"""
    try:
        with open(backup_file, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading backup data: {e}")
        sys.exit(1)

def filter_2fa_columns(data):
    """Filter out 2FA columns from the backup data"""
    # 2FA columns to remove
    twofa_columns = [
        'totp_secret',
        'totp_enabled',
        'backup_codes_hash',
        'totp_setup_completed',
        'can_enable_2fa'
    ]

    filtered_data = data.copy()

    if 'tables' in filtered_data:
        for table_name, table_data in filtered_data['tables'].items():
            if table_data and len(table_data) > 0:
                # Filter out 2FA columns from each record
                filtered_records = []
                for record in table_data:
                    filtered_record = {k: v for k, v in record.items() if k not in twofa_columns}
                    filtered_records.append(filtered_record)
                filtered_data['tables'][table_name] = filtered_records

    return filtered_data

def clear_existing_data(conn):
    """Clear existing data from all tables"""
    cursor = conn.cursor()

    print("Clearing existing data...")

    # Clear tables in reverse dependency order
    tables = [
        'activity_log',
        'password_history',
        'recruitment_document',
        'external_link',
        'recruitment_event',
        'university_contact',
        'cadet',
        'potential_recruit',
        'user'
    ]

    for table in tables:
        try:
            cursor.execute(f'DELETE FROM "{table}"')
            print(f"✓ Cleared {table}")
        except Exception as e:
            print(f"⚠ Error clearing {table}: {e}")

    # Reset sequences
    sequences = [
        'user_id_seq',
        'potential_recruit_id_seq',
        'cadet_id_seq',
        'university_contact_id_seq',
        'recruitment_event_id_seq',
        'external_link_id_seq',
        'recruitment_document_id_seq',
        'password_history_id_seq',
        'activity_log_id_seq'
    ]

    for seq in sequences:
        try:
            cursor.execute(f'ALTER SEQUENCE "{seq}" RESTART WITH 1')
            print(f"✓ Reset sequence {seq}")
        except Exception as e:
            print(f"⚠ Error resetting {seq}: {e}")

    conn.commit()
    cursor.close()

def restore_table_data(conn, table_name, data):
    """Restore data for a specific table"""
    cursor = conn.cursor()

    if not data:
        print(f"No data to restore for {table_name}")
        return 0

    try:
        # Get column names from the first record
        if not data:
            return 0

        columns = list(data[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([f'"{col}"' for col in columns])

        # Prepare values
        values = []
        for record in data:
            row_values = []
            for col in columns:
                value = record.get(col)
                # Handle None values and convert dates
                if value is None:
                    row_values.append(None)
                elif col in ['created_at', 'last_modified', 'password_changed_at', 'password_expires_at']:
                    try:
                        if isinstance(value, str):
                            row_values.append(value)
                        else:
                            row_values.append(value)
                    except:
                        row_values.append(None)
                else:
                    row_values.append(value)
            values.append(tuple(row_values))

        # Insert data
        insert_query = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'
        cursor.executemany(insert_query, values)

        restored_count = len(data)
        print(f"✓ Restored {restored_count} records to {table_name}")
        return restored_count

    except Exception as e:
        print(f"Error restoring {table_name}: {e}")
        return 0
    finally:
        cursor.close()

def main():
    """Main restore function"""
    print("Starting database restore from backup (2FA columns filtered)...")
    print("=" * 60)

    # Find latest backup
    backup_file = find_latest_backup()

    # Load backup data
    backup_data = load_backup_data(backup_file)
    print(f"Loaded backup from: {backup_data.get('timestamp', 'Unknown')}")
    print(f"Backup description: {backup_data.get('description', 'No description')}")

    # Filter out 2FA columns
    print("Filtering out 2FA columns from backup data...")
    filtered_data = filter_2fa_columns(backup_data)
    print("✓ 2FA columns filtered out")

    # Get database connection
    conn = get_database_connection()

    try:
        # Clear existing data
        clear_existing_data(conn)

        # Restore data for each table
        tables_data = filtered_data.get('tables', {})
        total_restored = 0

        # Restore in dependency order
        restore_order = [
            'user',
            'potential_recruit',
            'cadet',
            'university_contact',
            'recruitment_event',
            'external_link',
            'recruitment_document',
            'activity_log'
        ]

        for table_name in restore_order:
            if table_name in tables_data:
                restored_count = restore_table_data(conn, table_name, tables_data[table_name])
                total_restored += restored_count

        conn.commit()

        print("=" * 60)
        print(f"✓ Restore completed successfully!")
        print(f"✓ Total records restored: {total_restored}")
        print(f"✓ Source backup: {backup_file}")
        print(f"✓ 2FA columns were filtered out during restore")
        print("=" * 60)

    except Exception as e:
        print(f"Error during restore: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
