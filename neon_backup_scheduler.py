#!/usr/bin/env python3
"""
Enhanced Neon PostgreSQL Backup Scheduler for AFROTC 695 Recruitment System
This script runs nightly backups and weekly full backups using Vercel Blob storage with proper folder structure.
"""

import os
import sys
import time
import schedule
import threading
from datetime import datetime, timedelta
import json
import requests
import zipfile
import io
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from vercel_blob import put, list as blob_list, delete, head

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and database models
try:
    from api.app import app, db, User, PotentialRecruit, Cadet, UniversityContact, RecruitmentEvent, ExternalLink, RecruitmentDocument, ActivityLog, PasswordHistory
except ImportError:
    print("Error: Could not import Flask app. Make sure you're running from the project root.")
    sys.exit(1)

# Backup folder structure constants
BACKUP_FOLDERS = {
    'daily': 'backups',
    'full': 'backups/full'
}

def get_database_engine():
    """Get database engine for backup operations"""
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

def backup_database_neon(description="Nightly automatic backup", backup_type="daily"):
    """Create a PostgreSQL database backup with timestamp and description"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if backup_type == "full":
            backup_filename = f"{BACKUP_FOLDERS['full']}/afrotc695_full_backup_{timestamp}.json"
        else:
            backup_filename = f"{BACKUP_FOLDERS['daily']}/afrotc695_backup_{timestamp}.json"

        # Export all data to JSON format
        backup_data = {
            'timestamp': timestamp,
            'description': description,
            'backup_type': backup_type,
            'created_at': datetime.now().isoformat(),
            'tables': {}
        }

        # Get database engine
        engine = get_database_engine()
        if not engine:
            return None, None

        # Export each table
        tables = ['user', 'potential_recruit', 'cadet', 'university_contact',
                 'recruitment_event', 'external_link', 'recruitment_document',
                 'activity_log', 'password_history']

        with engine.connect() as connection:
            for table_name in tables:
                try:
                    # Use raw SQL to get all data
                    result = connection.execute(text(f'SELECT * FROM "{table_name}"'))
                    rows = [dict(row._mapping) for row in result]
                    backup_data['tables'][table_name] = rows
                    print(f"Backed up {len(rows)} records from {table_name}")
                except Exception as e:
                    print(f"Error backing up table {table_name}: {e}")
                    backup_data['tables'][table_name] = []

        # Convert to JSON string
        backup_json = json.dumps(backup_data, indent=2, default=str)

        # Upload to Vercel Blob
        blob_response = put(
            backup_filename,
            backup_json.encode('utf-8'),
            {"addRandomSuffix": False}
        )

        if blob_response and 'url' in blob_response:
            print(f"Backup uploaded successfully: {backup_filename}")
            return backup_filename, blob_response['url']
        else:
            print("Failed to upload backup to blob storage")
            return None, None

    except Exception as e:
        print(f"Error creating backup: {e}")
        return None, None

def create_full_backup_zip(description="Weekly full backup"):
    """Create a full backup that includes database and all blob contents"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"{BACKUP_FOLDERS['full']}/afrotc695_full_backup_{timestamp}.zip"

        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 1. Add database backup
            print("Creating database backup for full backup...")
            backup_filename, backup_url = backup_database_neon(description, "full")

            if backup_filename:
                # Get the database backup content and add to ZIP
                try:
                    db_backup_content = download_backup_file(backup_filename)
                    if db_backup_content:
                        zip_file.writestr('database_backup.json', db_backup_content)
                        print(f"Added database backup to ZIP: {backup_filename}")
                except Exception as e:
                    print(f"Error adding database backup to ZIP: {e}")

            # 2. Add all blob contents
            print("Adding all blob contents to full backup...")
            all_blob_files = blob_list()

            if isinstance(all_blob_files, list):
                blob_files = all_blob_files
            elif hasattr(all_blob_files, '__iter__') and not isinstance(all_blob_files, str):
                blob_files = list(all_blob_files)
            elif hasattr(all_blob_files, 'blobs'):
                blob_files = all_blob_files.blobs
            else:
                blob_files = []

            for blob_file in blob_files:
                try:
                    filename = blob_file.get('pathname', '') if isinstance(blob_file, dict) else str(blob_file)

                    # Skip the full backup we're creating
                    if filename == zip_filename:
                        continue

                    # Get the file content
                    file_content = download_backup_file(filename)
                    if file_content:
                        # Create a path within the ZIP that preserves folder structure
                        zip_path = f"blob_contents/{filename}"
                        zip_file.writestr(zip_path, file_content)
                        print(f"Added to ZIP: {filename}")

                except Exception as e:
                    print(f"Error adding {filename} to ZIP: {e}")
                    continue

            # 3. Add backup metadata
            metadata = {
                'timestamp': timestamp,
                'description': description,
                'backup_type': 'full',
                'created_at': datetime.now().isoformat(),
                'contents': {
                    'database_backup': backup_filename if backup_filename else None,
                    'blob_files_count': len(blob_files) if blob_files else 0,
                    'total_size': zip_buffer.tell()
                }
            }

            zip_file.writestr('backup_metadata.json', json.dumps(metadata, indent=2))

        # Upload the ZIP file
        zip_buffer.seek(0)
        zip_content = zip_buffer.read()

        blob_response = put(
            zip_filename,
            zip_content,
            {"addRandomSuffix": False}
        )

        if blob_response and 'url' in blob_response:
            print(f"Full backup ZIP uploaded successfully: {zip_filename}")
            return zip_filename, blob_response['url']
        else:
            print("Failed to upload full backup ZIP to blob storage")
            return None, None

    except Exception as e:
        print(f"Error creating full backup ZIP: {e}")
        return None, None

def list_backup_files():
    """List all backup files in blob storage with folder structure"""
    try:
        # Use the imported list function directly from vercel_blob
        blob_files = blob_list()

        # Handle different response types from vercel_blob
        if isinstance(blob_files, list):
            files = blob_files
        elif hasattr(blob_files, '__iter__') and not isinstance(blob_files, str):
            # It's some kind of iterable (list, tuple, etc.)
            files = list(blob_files)
        elif hasattr(blob_files, 'blobs'):
            # If it's an object with a blobs attribute
            files = blob_files.blobs
        else:
            print(f"Unexpected response type from blob.list(): {type(blob_files)}")
            return []

        # Process files to add metadata
        backup_files = []
        for file_info in files:
            try:
                filename = file_info.get('pathname', '') if isinstance(file_info, dict) else str(file_info)

                # Determine backup type based on filename
                if filename.startswith(f"{BACKUP_FOLDERS['full']}/"):
                    backup_type = "full"
                    if filename.endswith('.zip'):
                        backup_type = "full_zip"
                elif filename.startswith(f"{BACKUP_FOLDERS['daily']}/"):
                    backup_type = "daily"
                else:
                    # Skip files not in backup folders
                    continue

                # Extract timestamp and description
                timestamp = None
                description = "Unknown"

                if filename.endswith('.json'):
                    # Extract timestamp from filename: afrotc695_backup_YYYYMMDD_HHMMSS.json
                    if 'afrotc695_backup_' in filename:
                        timestamp_str = filename.split('afrotc695_backup_')[1].replace('.json', '')
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        except:
                            pass
                elif filename.endswith('.zip'):
                    # Extract timestamp from filename: afrotc695_full_backup_YYYYMMDD_HHMMSS.zip
                    if 'afrotc695_full_backup_' in filename:
                        timestamp_str = filename.split('afrotc695_full_backup_')[1].replace('.zip', '')
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        except:
                            pass

                # Get file size
                try:
                    file_info_obj = head(filename)
                    size = file_info_obj.get('size', 0) if isinstance(file_info_obj, dict) else 0
                except:
                    size = 0

                backup_files.append({
                    'filename': filename,
                    'backup_type': backup_type,
                    'created': timestamp,
                    'size': size,
                    'description': description,
                    'user': 'System'
                })

            except Exception as e:
                print(f"Error processing backup file {filename}: {e}")
                continue

        # Sort by creation date (newest first)
        backup_files.sort(key=lambda x: x['created'] if x['created'] else datetime.min, reverse=True)

        return backup_files

    except Exception as e:
        print(f"Error listing backup files: {e}")
        return []

def download_backup_file(filename):
    """Download a backup file from blob storage"""
    try:
        # Get file info first to get the URL
        file_info = head(filename)
        if file_info and 'url' in file_info:
            # Download the file content using requests
            import requests
            response = requests.get(file_info['url'])
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download file {filename}: HTTP {response.status_code}")
                return None
        else:
            print(f"Could not get file info for {filename}")
            return None
    except Exception as e:
        print(f"Error downloading backup file {filename}: {e}")
        return None

def delete_backup_file(filename):
    """Delete a backup file from blob storage"""
    try:
        delete(filename)
        print(f"Deleted backup file: {filename}")
        return True
    except Exception as e:
        print(f"Error deleting backup file {filename}: {e}")
        return False

def cleanup_old_backups():
    """Clean up backups older than 30 days (daily) and 90 days (full)"""
    try:
        print("Starting backup cleanup...")
        backup_files = list_backup_files()

        if not backup_files:
            print("No backup files found")
            return

        daily_cutoff = datetime.now() - timedelta(days=30)
        full_cutoff = datetime.now() - timedelta(days=90)
        deleted_count = 0

        for backup_file in backup_files:
            try:
                filename = backup_file['filename']
                backup_type = backup_file['backup_type']
                created = backup_file['created']

                if not created:
                    continue

                # Determine cutoff based on backup type
                if backup_type in ['full', 'full_zip']:
                    cutoff_date = full_cutoff
                else:
                    cutoff_date = daily_cutoff

                if created < cutoff_date:
                    if delete_backup_file(filename):
                        deleted_count += 1
                        print(f"Deleted old backup: {filename} (created: {created})")

            except Exception as e:
                print(f"Error processing backup file {filename}: {e}")
                continue

        print(f"Cleanup completed: {deleted_count} old backups deleted")

    except Exception as e:
        print(f"Error during backup cleanup: {e}")

def perform_nightly_backup():
    """Perform the nightly backup"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Starting nightly backup...")

    try:
        # Create daily backup
        backup_filename, backup_url = backup_database_neon("Nightly automatic backup", "daily")

        if backup_filename:
            print(f"[{timestamp}] Nightly backup completed successfully: {backup_filename}")
        else:
            print(f"[{timestamp}] Nightly backup failed")

    except Exception as e:
        print(f"[{timestamp}] Error during nightly backup: {e}")

def perform_weekly_full_backup():
    """Perform the weekly full backup"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Starting weekly full backup...")

    try:
        # Create full backup ZIP
        backup_filename, backup_url = create_full_backup_zip("Weekly full backup")

        if backup_filename:
            print(f"[{timestamp}] Weekly full backup completed successfully: {backup_filename}")
        else:
            print(f"[{timestamp}] Weekly full backup failed")

    except Exception as e:
        print(f"[{timestamp}] Error during weekly full backup: {e}")

def run_backup_scheduler():
    """Run the backup scheduler"""
    print("Starting AFROTC 695 Enhanced Neon Backup Scheduler...")
    print("Nightly backups will run at 2:00 AM")
    print("Weekly full backups will run at 3:00 AM on Sundays")
    print("Daily backup retention: 30 days")
    print("Full backup retention: 90 days")
    print("Storage: Vercel Blob with folder structure")
    print("Press Ctrl+C to stop the scheduler")

    # Schedule nightly backup at 2:00 AM
    schedule.every().day.at("02:00").do(perform_nightly_backup)

    # Schedule weekly full backup at 3:00 AM on Sundays
    schedule.every().sunday.at("03:00").do(perform_weekly_full_backup)

    # Schedule cleanup every day at 4:00 AM
    schedule.every().day.at("04:00").do(cleanup_old_backups)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nBackup scheduler stopped by user")
    except Exception as e:
        print(f"Error in backup scheduler: {e}")

def run_single_backup():
    """Run a single backup immediately"""
    print("Running immediate backup...")
    perform_nightly_backup()

def run_full_backup():
    """Run a full backup immediately"""
    print("Running immediate full backup...")
    perform_weekly_full_backup()

def test_backup_system():
    """Test the backup system"""
    print("Testing backup system...")

    # Test daily backup creation
    print("1. Testing daily backup creation...")
    backup_filename, backup_url = backup_database_neon("Test daily backup", "daily")
    if backup_filename:
        print(f"✅ Daily backup created: {backup_filename}")
    else:
        print("❌ Daily backup creation failed")
        return

    # Test full backup creation
    print("2. Testing full backup creation...")
    full_backup_filename, full_backup_url = create_full_backup_zip("Test full backup")
    if full_backup_filename:
        print(f"✅ Full backup created: {full_backup_filename}")
    else:
        print("❌ Full backup creation failed")

    # Test backup listing
    print("3. Testing backup listing...")
    backup_files = list_backup_files()
    print(f"✅ Found {len(backup_files)} backup files")

    # Test cleanup
    print("4. Testing cleanup (will not delete recent backups)...")
    cleanup_old_backups()
    print("✅ Cleanup test completed")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--now":
            # Run a single backup immediately
            run_single_backup()
        elif sys.argv[1] == "--full":
            # Run a full backup immediately
            run_full_backup()
        elif sys.argv[1] == "--test":
            # Test the backup system
            test_backup_system()
        else:
            print("Usage: python neon_backup_scheduler.py [--now|--full|--test]")
            print("  --now: Run a single daily backup immediately")
            print("  --full: Run a full backup immediately")
            print("  --test: Test the backup system")
    else:
        # Run the scheduled backup system
        run_backup_scheduler()
