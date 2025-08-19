#!/usr/bin/env python3
"""
Restore non-empty tables from a full backup ZIP file
"""

import os
import sys
import json
import zipfile
import io
import requests
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

try:
    from dotenv import load_dotenv
    load_dotenv()
    if os.path.exists("env.local"):
        load_dotenv()
except ImportError:
    pass


def get_database_engine():
    """Get database engine for restore operations"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        if not database_url:
            print("Error: DATABASE_URL environment variable not set")
            return None

        engine = create_engine(database_url)
        return engine
    except Exception as e:
        print(f"Error creating database engine: {e}")
        return None


def download_and_extract_backup(url):
    """Download backup ZIP and extract database_backup.json"""
    try:
        print(f"Downloading backup from: {url}")
        resp = requests.get(url, timeout=60)
        if resp.status_code != 200:
            print(f"Error: HTTP {resp.status_code} fetching backup")
            return None

        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        if "database_backup.json" not in zf.namelist():
            print("Error: database_backup.json not found in ZIP")
            return None

        data = zf.read("database_backup.json")
        backup_data = json.loads(data.decode("utf-8"))
        print(f"Successfully loaded backup: {backup_data.get('description', 'Unknown')}")
        return backup_data

    except Exception as e:
        print(f"Error downloading/extracting backup: {e}")
        return None


def restore_table(engine, table_name, rows, dry_run=True):
    """Restore a single table"""
    if not rows:
        print(f"  {table_name}: No data to restore (empty)")
        return 0

    print(f"  {table_name}: {len(rows)} records")

    if dry_run:
        print(f"    [DRY RUN] Would restore {len(rows)} records")
        return len(rows)

    try:
        with engine.begin() as connection:
            # Clear existing data (except for user table)
            if table_name != "user":
                connection.execute(text(f'DELETE FROM "{table_name}"'))
                print(f"    Cleared existing {table_name} data")

            # Insert new data
            if rows:
                # Get column names from first row
                columns = list(rows[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                column_list = ', '.join([f'"{col}"' for col in columns])
                insert_sql = f'INSERT INTO "{table_name}" ({column_list}) VALUES ({placeholders})'

                for row in rows:
                    # Convert datetime strings back to proper format if needed
                    processed_row = {}
                    for key, value in row.items():
                        if isinstance(value, str) and 'T' in value and value.endswith('Z'):
                            # Convert ISO format back to PostgreSQL format
                            try:
                                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                processed_row[key] = dt
                            except:
                                processed_row[key] = value
                        else:
                            processed_row[key] = value

                    connection.execute(text(insert_sql), processed_row)

                print(f"    Successfully restored {len(rows)} records")

        return len(rows)

    except Exception as e:
        print(f"    Error restoring {table_name}: {e}")
        return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/restore_from_backup.py <backup_zip_url> [--execute]")
        print("  --execute: Actually perform the restore (default is dry-run)")
        sys.exit(1)

    url = sys.argv[1]
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("=== DRY RUN MODE ===")
        print("No changes will be made to the database")
        print("Add --execute flag to perform actual restore")
        print()

    # Download and extract backup
    backup_data = download_and_extract_backup(url)
    if not backup_data:
        sys.exit(1)

    # Get database engine
    engine = get_database_engine()
    if not engine:
        sys.exit(1)

    # Tables to restore (excluding user table to preserve current admin)
    tables_to_restore = [
        'cadet',
        'university_contact',
        'recruitment_event',
        'external_link',
        'recruitment_document',
        'activity_log',
        'password_history'
    ]

    print(f"\nRestoring tables from backup...")
    total_restored = 0

    for table_name in tables_to_restore:
        rows = backup_data.get('tables', {}).get(table_name, [])
        restored_count = restore_table(engine, table_name, rows, dry_run)
        total_restored += restored_count

    print(f"\n=== RESTORE SUMMARY ===")
    print(f"Total records to restore: {total_restored}")
    if dry_run:
        print("This was a dry run. No changes were made.")
        print("Run with --execute flag to perform actual restore.")
    else:
        print("Restore completed successfully!")


if __name__ == "__main__":
    main()
