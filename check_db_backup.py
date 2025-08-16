#!/usr/bin/env python3
"""
Check SQLite database backups for potential recruit data
"""

import sqlite3
import os

def check_sqlite_backup(backup_file):
    """Check a SQLite backup file for potential recruit data"""
    print(f"\n=== Checking {backup_file} ===")

    if not os.path.exists(backup_file):
        print(f"File not found: {backup_file}")
        return

    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print(f"Tables found: {[table[0] for table in tables]}")

        # Check for potential_recruit table
        if any('potential' in table[0].lower() or 'recruit' in table[0].lower() for table in tables):
            print("Found potential recruit related table!")

            for table in tables:
                if 'potential' in table[0].lower() or 'recruit' in table[0].lower():
                    table_name = table[0]
                    print(f"\nChecking table: {table_name}")

                    # Get table schema
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    print("Columns:")
                    for col in columns:
                        print(f"  {col[1]} ({col[2]})")

                    # Get record count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"Record count: {count}")

                    if count > 0:
                        # Get sample data
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        records = cursor.fetchall()
                        print("Sample records:")
                        for record in records:
                            print(f"  {record}")

        # Check for any table with recruit in the name
        recruit_tables = [table[0] for table in tables if 'recruit' in table[0].lower()]
        if recruit_tables:
            print(f"\nRecruit-related tables found: {recruit_tables}")

        conn.close()

    except Exception as e:
        print(f"Error reading {backup_file}: {e}")

def main():
    """Check all SQLite backup files"""
    print("=== Checking SQLite Database Backups for Potential Recruits ===")

    backup_files = [
        "backups/afrotc695_backup_20250804_075339.db",
        "backups/afrotc695_backup_20250804_004033.db",
        "backups/afrotc695_backup_20250803_220937.db"
    ]

    for backup_file in backup_files:
        check_sqlite_backup(backup_file)

if __name__ == "__main__":
    main()
