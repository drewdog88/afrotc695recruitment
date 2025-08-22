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
import tarfile
import gzip
import io
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from vercel_blob import put, list as blob_list, delete, head
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and database models
try:
    from app import app, db, User, PotentialRecruit, Cadet, UniversityContact, RecruitmentEvent, ExternalLink, RecruitmentDocument, ActivityLog, PasswordHistory
except ImportError:
    print("Error: Could not import Flask app. Make sure you're running from the project root.")
    sys.exit(1)

# Backup folder structure constants
BACKUP_FOLDERS = {
    'daily': 'backups',
    'full': 'backups/full'
}

# Get blob store configuration from environment
BLOB_READ_WRITE_TOKEN = os.getenv('BLOB_READ_WRITE_TOKEN')
if not BLOB_READ_WRITE_TOKEN:
    print("Warning: BLOB_READ_WRITE_TOKEN not set - backup system unavailable")

def get_r2_client():
    """Get configured R2 client using boto3 with custom domain for enhanced security"""
    try:
        # Use custom domain if configured, otherwise fall back to direct R2 endpoint
        custom_domain = os.getenv('CLOUDFLARE_R2_CUSTOM_DOMAIN')

        if custom_domain:
            # Use custom domain with Cloudflare Access protection
            endpoint_url = f'https://{custom_domain}'
            print(f"Using secure custom domain: {endpoint_url}")
        else:
            # Fall back to direct R2 endpoint (less secure)
            endpoint_url = f'https://{os.getenv("CLOUDFLARE_R2_ACCOUNT_ID")}.r2.cloudflarestorage.com'
            print(f"Warning: Using direct R2 endpoint. Consider setting CLOUDFLARE_R2_CUSTOM_DOMAIN for enhanced security")

        return boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
            region_name='auto'
        )
    except Exception as e:
        print(f"Error creating R2 client: {e}")
        return None

def upload_backup_to_r2(backup_data, filename):
    """Upload backup to R2 using boto3"""
    try:
        r2_client = get_r2_client()
        bucket_name = 'afrotc695recruitment'

        r2_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=backup_data
        )
        return True
    except ClientError as e:
        print(f"R2 upload error: {e}")
        return False

def list_backup_files_r2():
    """List backup files in R2 using boto3"""
    try:
        r2_client = get_r2_client()
        bucket_name = 'afrotc695recruitment'

        response = r2_client.list_objects_v2(
            Bucket=bucket_name
            # Removed restrictive prefix filter to list all files
        )

        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                # Only include backup-related files
                if 'backup' in obj['Key'].lower() or 'afrotc695' in obj['Key'].lower():
                    files.append({
                        'filename': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
        return files
    except ClientError as e:
        print(f"R2 list error: {e}")
        return []

def download_backup_file_r2(filename):
    """Download backup file from R2 using boto3 with enhanced security validation"""
    try:
        r2_client = get_r2_client()
        if not r2_client:
            print("Error: Failed to create R2 client")
            return None

        bucket_name = 'afrotc695recruitment'

        # Security validation: Ensure filename is safe
        if not filename or '..' in filename or filename.startswith('/'):
            print(f"Security error: Invalid filename pattern: {filename}")
            return None

        # Security validation: Only allow backup files
        if not filename.startswith('afrotc695_backup_'):
            print(f"Security error: Filename does not match backup pattern: {filename}")
            return None

        response = r2_client.get_object(
            Bucket=bucket_name,
            Key=filename
        )

        content = response['Body'].read()
        print(f"Successfully downloaded {len(content)} bytes from R2: {filename}")
        return content

    except ClientError as e:
        print(f"R2 download error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error downloading from R2: {e}")
        return None

# R2 Configuration
R2_BUCKET_NAME = 'afrotc695recruitment'

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
        # Use flat R2 filename structure (no folders)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # e.g., 20250110_143022

        if backup_type == "full":
            backup_filename = f"afrotc695_backup_full_{timestamp}.json"
        else:
            backup_filename = f"afrotc695_backup_daily_{timestamp}.json"

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

        # Upload to R2 (replacing Vercel Blob)
        success = upload_backup_to_r2(backup_json.encode('utf-8'), backup_filename)

        if success:
            print(f"Backup uploaded successfully to R2: {backup_filename}")
            # Return filename and a placeholder URL (R2 doesn't provide direct URLs)
            return backup_filename, f"r2://{backup_filename}"
        else:
            print("Failed to upload backup to R2 storage")
            return None, None

    except Exception as e:
        print(f"Error creating backup: {e}")
        return None, None

def create_full_backup_tgz(description="Weekly full backup"):
    """Create a full backup that includes database, Vercel Blob contents, and R2 backup files using tar.gz format"""
    try:
        # Use flat R2 filename structure (no folders)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # e.g., 20250110_143022
        tgz_filename = f"afrotc695_backup_full_{timestamp}.tar.gz"

        # Create a tar.gz file in memory
        tgz_buffer = io.BytesIO()

        with tarfile.open(fileobj=tgz_buffer, mode='w:gz') as tar_file:
            # 1. Add database backup
            print("Creating database backup for full backup...")
            backup_filename, backup_url = backup_database_neon(description, "full")

            if backup_filename and backup_url:
                # Get the database backup content and add to tar.gz
                try:
                    # Since we're using R2 now, download from R2
                    db_backup_content = download_backup_file_r2(backup_filename)
                    if db_backup_content:
                        # Create a TarInfo object for the database backup
                        db_info = tarfile.TarInfo(name='database_backup.json')
                        db_info.size = len(db_backup_content)
                        tar_file.addfile(db_info, io.BytesIO(db_backup_content))
                        print(f"Added database backup to tar.gz: {backup_filename}")
                    else:
                        print(f"Failed to download database backup content from R2: {backup_filename}")
                except Exception as e:
                    print(f"Error adding database backup to tar.gz: {e}")

            # 2. Add all Vercel Blob contents (existing documents)
            print("Adding all Vercel Blob contents to full backup...")
            all_blob_files = blob_list()

            # Fix blob list extraction - blob_list() returns dict with 'blobs' key
            if isinstance(all_blob_files, dict) and 'blobs' in all_blob_files:
                blob_files = all_blob_files['blobs']
            elif isinstance(all_blob_files, list):
                blob_files = all_blob_files
            else:
                print(f"Unexpected blob_list() response type: {type(all_blob_files)}")
                blob_files = []

            print(f"Found {len(blob_files)} files in Vercel Blob storage")

            for blob_file in blob_files:
                try:
                    # Extract filename and URL from blob object
                    if isinstance(blob_file, dict):
                        filename = blob_file.get('pathname', '')
                        blob_url = blob_file.get('url', '')
                    else:
                        filename = str(blob_file)
                        blob_url = None

                    # Skip the full backup we're creating (more robust check)
                    if filename == tgz_filename or (filename.endswith('.tar.gz') and 'blob-backup-' in filename):
                        print(f"Skipping self-reference: {filename}")
                        continue

                    # Skip any prior backup artifacts to avoid recursive growth
                    # This excludes anything under backups/ (daily or full)
                    if filename.startswith('backups/'):
                        # Still allow including the database backup JSON we just created (added separately above)
                        # All other backup artifacts are excluded from the full-blob archive
                        print(f"Skipping backup artifact: {filename}")
                        continue

                    # Skip if no URL available
                    if not blob_url:
                        print(f"No URL available for {filename}, skipping")
                        continue

                    # Optional: Check blob store host if configured (for Vercel Blob security)
                    # Since we're migrating to R2, this check is less critical but kept for security
                    vercel_blob_host = os.getenv('BLOB_STORE_HOST', 'kre9xoivjggj03of.public.blob.vercel-storage.com')
                    if vercel_blob_host:
                        try:
                            parsed = urlparse(blob_url)
                            if parsed.netloc != vercel_blob_host:
                                print(f"Skipping file from unexpected host {parsed.netloc}: {filename}")
                                continue
                        except Exception as e:
                            print(f"Error parsing URL for {filename}: {e}")
                            continue

                    # Get the file content using the blob URL
                    file_content = download_backup_file_by_url(blob_url)
                    if file_content:
                        # Create a path within the tar.gz that preserves folder structure
                        tar_path = f"vercel_blob_contents/{filename}"
                        # Create a TarInfo object for the file
                        file_info = tarfile.TarInfo(name=tar_path)
                        file_info.size = len(file_content)
                        tar_file.addfile(file_info, io.BytesIO(file_content))
                        print(f"Added Vercel Blob file to tar.gz: {filename} ({len(file_content)} bytes)")
                    else:
                        print(f"Failed to download content for {filename}")

                except Exception as e:
                    print(f"Error adding {filename} to tar.gz: {e}")
                    continue

            # 3. Add all R2 backup files (existing backups)
            print("Adding all R2 backup files to full backup...")
            r2_backup_files = list_backup_files_r2()
            print(f"Found {len(r2_backup_files)} backup files in R2 storage")

            for r2_file in r2_backup_files:
                try:
                    filename = r2_file['filename']

                    # Skip the full backup we're creating (prevent recursive backup)
                    if filename == tgz_filename:
                        print(f"Skipping self-reference: {filename}")
                        continue

                    # Skip other full backups to prevent recursive growth
                    if filename.startswith('afrotc695_backup_full_'):
                        print(f"Skipping existing full backup: {filename}")
                        continue

                    # Get the file content from R2
                    file_content = download_backup_file_r2(filename)
                    if file_content:
                        # Create a path within the tar.gz for R2 backups
                        tar_path = f"r2_backup_files/{filename}"
                        # Create a TarInfo object for the file
                        file_info = tarfile.TarInfo(name=tar_path)
                        file_info.size = len(file_content)
                        tar_file.addfile(file_info, io.BytesIO(file_content))
                        print(f"Added R2 backup file to tar.gz: {filename} ({len(file_content)} bytes)")
                    else:
                        print(f"Failed to download R2 backup file: {filename}")

                except Exception as e:
                    print(f"Error adding R2 backup file {filename} to tar.gz: {e}")
                    continue

            # 4. Add backup metadata
            metadata = {
                'timestamp': timestamp,
                'description': description,
                'backup_type': 'full',
                'created_at': datetime.now().isoformat(),
                'contents': {
                    'database_backup': backup_filename if backup_filename else None,
                    'vercel_blob_files_count': len(blob_files) if blob_files else 0,
                    'r2_backup_files_count': len(r2_backup_files) if r2_backup_files else 0,
                    'total_size': tgz_buffer.tell()
                }
            }

            # Create a TarInfo object for the metadata
            metadata_content = json.dumps(metadata, indent=2).encode('utf-8')
            metadata_info = tarfile.TarInfo(name='backup_metadata.json')
            metadata_info.size = len(metadata_content)
            tar_file.addfile(metadata_info, io.BytesIO(metadata_content))

        # Upload the tar.gz file to R2
        tgz_buffer.seek(0)
        tgz_content = tgz_buffer.read()

        success = upload_backup_to_r2(tgz_content, tgz_filename)

        if success:
            print(f"Full backup tar.gz uploaded successfully to R2: {tgz_filename}")
            return tgz_filename, f"r2://{tgz_filename}"  # Placeholder URL
        else:
            print("Failed to upload full backup tar.gz to R2 storage")
            return None, None

    except Exception as e:
        print(f"Error creating full backup tar.gz: {e}")
        return None, None

def list_backup_files():
    """List all backup files in R2 storage (replacing Vercel Blob)"""
    try:
        # Use R2 listing instead of Vercel Blob
        r2_files = list_backup_files_r2()

        if not r2_files:
            print("No backup files found in R2 storage")
            return []

        # Process R2 files to add metadata
        backup_files = []
        for file_info in r2_files:
            try:
                filename = file_info['filename']  # R2 returns filename directly

                # Determine backup type based on flat filename structure
                backup_type = "unknown"
                if filename.endswith('.tar.gz'):
                    backup_type = "full"
                elif filename.endswith('.json'):
                    if 'daily' in filename:
                        backup_type = "daily"
                    elif 'full' in filename:
                        backup_type = "full"
                    else:
                        backup_type = "daily"  # Default for JSON files

                # Extract timestamp and description
                timestamp = None
                description = "Unknown"

                if filename.endswith('.json'):
                    # Extract timestamp from filename: afrotc695_backup_daily_YYYYMMDD_HHMMSS.json
                    # or afrotc695_backup_full_YYYYMMDD_HHMMSS.json
                    if 'afrotc695_backup_' in filename:
                        # Remove prefix and extension
                        timestamp_part = filename.replace('afrotc695_backup_daily_', '').replace('afrotc695_backup_full_', '').replace('.json', '')
                        try:
                            timestamp = datetime.strptime(timestamp_part, '%Y%m%d_%H%M%S')
                        except:
                            pass

                    # Try to read description from the JSON backup file
                    try:
                        backup_content = download_backup_file(filename)
                        if backup_content:
                            backup_data = json.loads(backup_content.decode('utf-8'))
                            if 'description' in backup_data:
                                description = backup_data['description']
                    except Exception as e:
                        print(f"Could not read description from {filename}: {e}")

                elif filename.endswith('.tar.gz'):
                    # Extract timestamp from filename: afrotc695_backup_full_YYYYMMDD_HHMMSS.tar.gz
                    if 'afrotc695_backup_full_' in filename:
                        timestamp_part = filename.replace('afrotc695_backup_full_', '').replace('.tar.gz', '')
                        try:
                            timestamp = datetime.strptime(timestamp_part, '%Y%m%d_%H%M%S')
                        except:
                            pass

                    # Try to read description from the tar.gz metadata
                    try:
                        backup_content = download_backup_file(filename)
                        if backup_content:
                            import tarfile
                            import io
                            with tarfile.open(fileobj=io.BytesIO(backup_content), mode='r:gz') as tar_file:
                                if 'backup_metadata.json' in [member.name for member in tar_file.getmembers()]:
                                    metadata_content = tar_file.extractfile('backup_metadata.json').read()
                                    metadata = json.loads(metadata_content.decode('utf-8'))
                                    if 'description' in metadata:
                                        description = metadata['description']
                    except Exception as e:
                        print(f"Could not read description from tar.gz {filename}: {e}")

                # Get file size from R2 metadata
                size = file_info.get('size', 0)  # R2 provides size directly

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
    """Download a backup file from R2 storage (replacing Vercel Blob)"""
    try:
        # Use R2 download instead of Vercel Blob
        content = download_backup_file_r2(filename)
        if content:
            return content
        else:
            print(f"Failed to download file {filename} from R2")
            return None
    except Exception as e:
        print(f"Error downloading backup file {filename} from R2: {e}")
        return None

def download_backup_file_by_url(url):
    """Download a file directly from its blob URL"""
    try:
        import requests
        # Stream with sensible timeouts to avoid long hangs on huge files
        with requests.get(url, stream=True, timeout=(10, 60)) as response:
            if response.status_code != 200:
                print(f"Failed to download file from {url}: HTTP {response.status_code}")
                return None
            content = io.BytesIO()
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                if chunk:
                    content.write(chunk)
            return content.getvalue()
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")
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
        backup_filename, backup_url = create_full_backup_tgz("Weekly full backup")

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
    print("Storage: Cloudflare R2 with flat filename structure")
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
    full_backup_filename, full_backup_url = create_full_backup_tgz("Test full backup")
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
