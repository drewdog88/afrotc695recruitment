#!/usr/bin/env python3
"""
Scheduled Backup Script for AFROTC 695 Recruitment System
This script runs nightly backups when the server is running.
"""

import os
import sys
import time
import schedule
import threading
from datetime import datetime
import sqlite3
import shutil
import json

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Database backup configuration
BACKUP_DIR = 'backups'
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def backup_database_standalone(description="Nightly automatic backup"):
    """Create a database backup with timestamp and description (standalone version)"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"afrotc695_backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Get the current database path
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'afrotc695.db')
        
        # Create backup
        shutil.copy2(db_path, backup_path)
        
        # Create backup metadata
        metadata = {
            'timestamp': timestamp,
            'description': description,
            'filename': backup_filename,
            'size': os.path.getsize(backup_path),
            'user': 'Scheduled Backup System'
        }
        
        # Save metadata to a JSON file
        metadata_file = backup_path.replace('.db', '_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Database backup created: {backup_filename}")
        return backup_filename, backup_path
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None, None

def check_server_running():
    """Check if the Flask server is running by trying to connect to the database"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'afrotc695.db')
        conn = sqlite3.connect(db_path)
        conn.close()
        return True
    except Exception as e:
        print(f"Server not running or database not accessible: {e}")
        return False

def perform_nightly_backup():
    """Perform the nightly backup if the server is running"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Starting nightly backup...")
    
    if not check_server_running():
        print(f"[{timestamp}] Server not running, skipping backup")
        return
    
    try:
        # Create backup with description
        backup_filename, backup_path = backup_database_standalone("Nightly automatic backup")
        
        if backup_filename:
            print(f"[{timestamp}] Nightly backup completed successfully: {backup_filename}")
            
            # Clean up old backups (keep last 7 days)
            cleanup_old_backups()
        else:
            print(f"[{timestamp}] Nightly backup failed")
            
    except Exception as e:
        print(f"[{timestamp}] Error during nightly backup: {e}")

def cleanup_old_backups():
    """Clean up backups older than 7 days"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.db'):
                backup_path = os.path.join(BACKUP_DIR, filename)
                file_modified = datetime.fromtimestamp(os.path.getmtime(backup_path))
                
                if file_modified < cutoff_date:
                    # Remove the backup file and its metadata
                    os.remove(backup_path)
                    metadata_file = backup_path.replace('.db', '_metadata.json')
                    if os.path.exists(metadata_file):
                        os.remove(metadata_file)
                    print(f"Cleaned up old backup: {filename}")
                    
    except Exception as e:
        print(f"Error during backup cleanup: {e}")

def run_backup_scheduler():
    """Run the backup scheduler"""
    print("Starting AFROTC 695 Backup Scheduler...")
    print("Nightly backups will run at 2:00 AM")
    print("Additional backups will run every 6 hours during the day")
    print("Press Ctrl+C to stop the scheduler")
    
    # Schedule nightly backup at 2:00 AM
    schedule.every().day.at("02:00").do(perform_nightly_backup)
    
    # Also run a backup every 6 hours during the day for additional safety
    schedule.every(6).hours.do(perform_nightly_backup)
    
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

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # Run a single backup immediately
        run_single_backup()
    else:
        # Run the scheduled backup system
        run_backup_scheduler() 