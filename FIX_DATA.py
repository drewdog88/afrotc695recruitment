#!/usr/bin/env python3
"""
🚨 ONE-COMMAND DATA FIX
Run this when Cursor/AI breaks your data!
Usage: python FIX_DATA.py
"""

import json
import psycopg2
from pathlib import Path

# Direct database URL
DATABASE_URL = "postgresql://neondb_owner:npg_5qC7jUoluvOY@ep-crimson-hall-admf1mo5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def fix_data():
    """Fix data in one command"""
    print("🚨 FIXING YOUR DATA...")
    print("=" * 50)

    # Find most recent backup
    backup_dir = Path("backups")
    backup_files = list(backup_dir.glob("*.json"))

    if not backup_files:
        print("❌ No backup files found!")
        return

    # Get the most recent backup (excluding metadata files)
    valid_backups = [f for f in backup_files if not f.name.endswith('_metadata.json')]
    if not valid_backups:
        print("❌ No valid backup files found!")
        return

    # Sort by modification time (newest first)
    valid_backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    backup_file = valid_backups[0]

    print(f"📂 Using backup: {backup_file.name}")

    # Load backup data
    try:
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading backup: {e}")
        return

    print(f"📊 Backup contains {sum(len(records) for records in backup_data['tables'].values())} records")

    # Connect to database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    try:
        # Restore main tables
        main_tables = ['cadet', 'university_contact', 'potential_recruit', 'recruitment_event', 'external_link', 'recruitment_document']
        restored_count = 0

        for table_name in main_tables:
            if table_name not in backup_data['tables'] or not backup_data['tables'][table_name]:
                continue

            records = backup_data['tables'][table_name]
            print(f"🔄 Restoring {table_name}: {len(records)} records")

            # Clear and restore
            cursor.execute(f"DELETE FROM {table_name}")

            for record in records:
                try:
                    columns = list(record.keys())
                    values = list(record.values())
                    placeholders = ', '.join(['%s'] * len(values))
                    column_list = ', '.join(columns)

                    query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
                    cursor.execute(query, values)
                    restored_count += 1
                except Exception as e:
                    continue

        # Commit changes
        conn.commit()
        print(f"\n✅ FIXED! Restored {restored_count} records")

        # Quick verification
        print("\n🔍 Verification:")
        for table_name in main_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {table_name}: {count} records")

    except Exception as e:
        print(f"❌ Fix failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("🔌 Disconnected")

if __name__ == "__main__":
    fix_data()
