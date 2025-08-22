#!/usr/bin/env python3
"""
Migrate all backup files from Vercel Blob to Cloudflare R2
This script downloads all backup files from Vercel Blob and uploads them to R2
"""

import os
import sys
import json
import requests
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import tempfile
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Vercel Blob configuration
BLOB_READ_WRITE_TOKEN = os.getenv('BLOB_READ_WRITE_TOKEN')
if not BLOB_READ_WRITE_TOKEN:
    print("❌ Error: BLOB_READ_WRITE_TOKEN not found in environment variables")
    sys.exit(1)

# Cloudflare R2 configuration
R2_ACCOUNT_ID = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.getenv('CLOUDFLARE_R2_BUCKET_NAME', 'afrotc695recruitment')

if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
    print("❌ Error: Cloudflare R2 credentials not found in environment variables")
    print("Please set: CLOUDFLARE_R2_ACCOUNT_ID, CLOUDFLARE_R2_ACCESS_KEY_ID, CLOUDFLARE_R2_SECRET_ACCESS_KEY")
    sys.exit(1)

def get_vercel_blob_files():
    """Get list of all files in Vercel Blob storage"""
    try:
        url = "https://blob.vercel-storage.com"
        headers = {
            'Authorization': f'Bearer {BLOB_READ_WRITE_TOKEN}'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            blob_data = response.json()
            if 'blobs' in blob_data:
                return blob_data['blobs']
            else:
                print(f"❌ Unexpected response format: {blob_data}")
                return []
        else:
            print(f"❌ Failed to get blob files: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting blob files: {e}")
        return []

def download_blob_file(filename):
    """Download a file from Vercel Blob storage"""
    try:
        url = f"https://blob.vercel-storage.com/{filename}"
        headers = {
            'Authorization': f'Bearer {BLOB_READ_WRITE_TOKEN}'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print(f"❌ Failed to download {filename}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")
        return None

def upload_to_r2(filename, content):
    """Upload a file to Cloudflare R2"""
    try:
        # Create R2 client
        r2_client = boto3.client(
            's3',
            endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            region_name='auto'
        )

        # Upload file (no folder structure, just filename)
        r2_client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=filename,
            Body=content
        )

        print(f"✅ Uploaded to R2: {filename}")
        return True
    except ClientError as e:
        print(f"❌ R2 upload error for {filename}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error uploading {filename}: {e}")
        return False

def is_backup_file(filename):
    """Check if a file is a backup file"""
    backup_indicators = [
        'backup',
        'afrotc695',
        'db-backup',
        'blob-backup'
    ]

    filename_lower = filename.lower()
    return any(indicator in filename_lower for indicator in backup_indicators)

def main():
    """Main migration function"""
    print("=== AFROTC 695 Backup Migration to Cloudflare R2 ===")
    print(f"Source: Vercel Blob")
    print(f"Destination: Cloudflare R2 bucket '{R2_BUCKET_NAME}'")
    print()

    # Get all files from Vercel Blob
    print("📡 Getting list of files from Vercel Blob...")
    blob_files = get_vercel_blob_files()

    if not blob_files:
        print("❌ No files found in Vercel Blob or error occurred")
        return

    print(f"📁 Found {len(blob_files)} files in Vercel Blob")

    # Filter for backup files
    backup_files = []
    for file_info in blob_files:
        if isinstance(file_info, dict):
            filename = file_info.get('pathname', '')
        else:
            filename = str(file_info)

        if is_backup_file(filename):
            backup_files.append(filename)

    print(f"🔒 Found {len(backup_files)} backup files to migrate")

    if not backup_files:
        print("❌ No backup files found to migrate")
        return

    # Create temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📂 Using temporary directory: {temp_dir}")

        # Download and upload each backup file
        successful_migrations = 0
        failed_migrations = 0

        for i, filename in enumerate(backup_files, 1):
            print(f"\n[{i}/{len(backup_files)}] Processing: {filename}")

            # Download from Vercel Blob
            print(f"  📥 Downloading from Vercel Blob...")
            content = download_blob_file(filename)

            if content is None:
                print(f"  ❌ Failed to download {filename}")
                failed_migrations += 1
                continue

            print(f"  📦 Downloaded {len(content)} bytes")

            # Upload to R2
            print(f"  📤 Uploading to Cloudflare R2...")
            if upload_to_r2(filename, content):
                successful_migrations += 1
            else:
                failed_migrations += 1

        # Summary
        print(f"\n=== Migration Summary ===")
        print(f"✅ Successful migrations: {successful_migrations}")
        print(f"❌ Failed migrations: {failed_migrations}")
        print(f"📊 Total processed: {len(backup_files)}")

        if successful_migrations > 0:
            print(f"\n🎉 Successfully migrated {successful_migrations} backup files to Cloudflare R2!")
            print(f"📁 All backup files are now stored in bucket: {R2_BUCKET_NAME}")
        else:
            print(f"\n❌ No files were successfully migrated")

if __name__ == "__main__":
    main()

