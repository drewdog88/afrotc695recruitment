#!/usr/bin/env python3
"""
AFROTC 695 Data Recovery System
Use this whenever Cursor/AI breaks your data!
"""

import json
import psycopg2
import os
from datetime import datetime
from pathlib import Path

# Direct database URL from env.local
DATABASE_URL = "postgresql://neondb_owner:npg_5qC7jUoluvOY@ep-crimson-hall-admf1mo5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

class DataRecoverySystem:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.conn = None
        self.cursor = None

    def connect_db(self):
        """Connect to production database"""
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.cursor = self.conn.cursor()
            print("✅ Connected to production database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def disconnect_db(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Disconnected from database")

    def list_backups(self):
        """List all available backups"""
        print("📂 Available Backups:")
        print("=" * 50)

        backups = []
        for file in self.backup_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    total_records = sum(len(records) for records in data['tables'].values())
                    backups.append({
                        'file': file.name,
                        'timestamp': data.get('timestamp', 'Unknown'),
                        'description': data.get('description', 'No description'),
                        'records': total_records,
                        'size': file.stat().st_size
                    })
            except Exception as e:
                print(f"⚠️  Error reading {file.name}: {e}")

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)

        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup['file']}")
            print(f"   📅 {backup['timestamp']}")
            print(f"   📝 {backup['description']}")
            print(f"   📊 {backup['records']} records")
            print(f"   📦 {backup['size']} bytes")
            print()

        return backups

    def check_current_db_state(self):
        """Check current database state"""
        if not self.connect_db():
            return

        print("🔍 Current Database State:")
        print("=" * 50)

        # Get all tables
        self.cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = [row[0] for row in self.cursor.fetchall()]

        total_records = 0
        key_tables = ['user', 'cadet', 'university_contact', 'potential_recruit']

        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            total_records += count

            status = "✅" if count > 0 else "⚠️"
            if table in key_tables:
                status = "✅" if count > 0 else "❌"

            print(f"{status} {table}: {count} records")

        print(f"\n📊 Total records: {total_records}")

        # Check if data is missing
        missing_data = False
        for table in key_tables:
            if table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                if count == 0:
                    missing_data = True
                    break

        if missing_data:
            print("\n🚨 DATA LOSS DETECTED! Use recovery mode.")
        else:
            print("\n✅ Database appears healthy")

        self.disconnect_db()

    def recover_from_backup(self, backup_file=None):
        """Recover data from a specific backup"""
        if not backup_file:
            # Use the most recent backup
            backups = list(self.backup_dir.glob("*.json"))
            if not backups:
                print("❌ No backup files found!")
                return False

            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            backup_file = backups[0]

        print(f"🔄 Starting recovery from: {backup_file.name}")
        print("=" * 60)

        # Load backup data
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading backup: {e}")
            return False

        print(f"📊 Backup contains {sum(len(records) for records in backup_data['tables'].values())} total records")

        # Connect to database
        if not self.connect_db():
            return False

        try:
            # Define restore order (independent tables first)
            restore_order = [
                'cadet',
                'university_contact',
                'potential_recruit',
                'recruitment_event',
                'external_link',
                'recruitment_document'
            ]

            restored_count = 0

            for table_name in restore_order:
                if table_name not in backup_data['tables'] or not backup_data['tables'][table_name]:
                    print(f"⏭️  Skipping {table_name} (no data)")
                    continue

                records = backup_data['tables'][table_name]
                print(f"🔄 Restoring {table_name}: {len(records)} records")

                # Clear existing data
                self.cursor.execute(f"DELETE FROM {table_name}")
                print(f"   🗑️  Cleared existing {table_name} data")

                # Insert new records
                success_count = 0
                for record in records:
                    try:
                        columns = list(record.keys())
                        values = list(record.values())
                        placeholders = ', '.join(['%s'] * len(values))
                        column_list = ', '.join(columns)

                        query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
                        self.cursor.execute(query, values)
                        success_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Error inserting record: {e}")
                        continue

                print(f"   ✅ Restored {success_count}/{len(records)} records to {table_name}")
                restored_count += success_count

            # Commit changes
            self.conn.commit()
            print(f"\n✅ Recovery completed! Restored {restored_count} records")

            # Verify recovery
            print("\n🔍 Recovery Verification:")
            for table_name in restore_order:
                if table_name in backup_data['tables']:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = self.cursor.fetchone()[0]
                    print(f"   {table_name}: {count} records")

            return True

        except Exception as e:
            print(f"❌ Recovery failed: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect_db()

    def create_backup_now(self):
        """Create a backup of current state"""
        if not self.connect_db():
            return False

        print("📸 Creating backup of current state...")

        try:
            # Get all tables
            self.cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)

            tables = [row[0] for row in self.cursor.fetchall()]

            backup_data = {
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'description': 'Emergency backup before recovery',
                'created_at': datetime.now().isoformat(),
                'tables': {}
            }

            for table in tables:
                self.cursor.execute(f"SELECT * FROM {table}")
                columns = [desc[0] for desc in self.cursor.description]
                rows = self.cursor.fetchall()

                records = []
                for row in rows:
                    record = dict(zip(columns, row))
                    records.append(record)

                backup_data['tables'][table] = records

            # Save backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"emergency_backup_{timestamp}.json"

            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)

            print(f"✅ Emergency backup created: {backup_file.name}")
            print(f"📊 Contains {sum(len(records) for records in backup_data['tables'].values())} records")

            return True

        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False
        finally:
            self.disconnect_db()

def main():
    """Main recovery interface"""
    recovery = DataRecoverySystem()

    print("🚨 AFROTC 695 Data Recovery System")
    print("=" * 50)
    print("Use this when Cursor/AI breaks your data!")
    print()

    while True:
        print("\n📋 Recovery Options:")
        print("1. Check current database state")
        print("2. List available backups")
        print("3. Recover from most recent backup")
        print("4. Recover from specific backup")
        print("5. Create emergency backup")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == '1':
            recovery.check_current_db_state()

        elif choice == '2':
            recovery.list_backups()

        elif choice == '3':
            print("\n🔄 Recovering from most recent backup...")
            recovery.recover_from_backup()

        elif choice == '4':
            backups = recovery.list_backups()
            if backups:
                try:
                    backup_num = int(input("Enter backup number: ")) - 1
                    if 0 <= backup_num < len(backups):
                        backup_file = recovery.backup_dir / backups[backup_num]['file']
                        print(f"\n🔄 Recovering from {backup_file.name}...")
                        recovery.recover_from_backup(backup_file)
                    else:
                        print("❌ Invalid backup number")
                except ValueError:
                    print("❌ Please enter a valid number")

        elif choice == '5':
            recovery.create_backup_now()

        elif choice == '6':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
