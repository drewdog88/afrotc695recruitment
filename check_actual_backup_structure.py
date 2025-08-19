#!/usr/bin/env python3
"""
Check the actual backup structure in Vercel Blob storage
"""

import os
from dotenv import load_dotenv
from vercel_blob import list as blob_list

# Load environment variables from .env
load_dotenv()

def check_backup_structure():
    """Check the actual backup structure on the blob store"""
    try:
        print("Checking backup structure on blob store...")

        # List all files in the blob store
        blobs = blob_list()

        if not blobs:
            print("❌ No files found in blob store")
            return

        print(f"Found {len(blobs)} files in blob store")

        # Group files by directory structure
        backup_files = []
        other_files = []

        for blob in blobs:
            if blob.pathname.startswith('backups/'):
                backup_files.append(blob.pathname)
            else:
                other_files.append(blob.pathname)

        print(f"\n📁 BACKUP FILES ({len(backup_files)}):")
        if backup_files:
            for file in sorted(backup_files):
                print(f"  {file}")
        else:
            print("  No backup files found")

        print(f"\n📄 OTHER FILES ({len(other_files)}):")
        if other_files:
            for file in sorted(other_files):
                print(f"  {file}")
        else:
            print("  No other files found")

        # Check for date-organized structure
        date_folders = set()
        for file in backup_files:
            parts = file.split('/')
            if len(parts) >= 3 and parts[0] == 'backups':
                if len(parts) >= 3:
                    date_folders.add(parts[2])  # backups/type/date/

        print(f"\n📅 DATE FOLDERS FOUND:")
        if date_folders:
            for date in sorted(date_folders):
                print(f"  {date}")
        else:
            print("  No date-organized folders found")

    except Exception as e:
        print(f"Error checking backup structure: {e}")

if __name__ == "__main__":
    check_backup_structure()
