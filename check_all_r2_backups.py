#!/usr/bin/env python3
"""
Check ALL files in R2 bucket to find any backup files
"""

import os
import boto3
from datetime import datetime
from dotenv import load_dotenv

def main():
    load_dotenv()

    print("Checking ALL files in R2 bucket...")

    try:
        # Create R2 client
        r2_client = boto3.client(
            's3',
            endpoint_url=f'https://{os.getenv("CLOUDFLARE_R2_ACCOUNT_ID")}.r2.cloudflarestorage.com',
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
            region_name='auto'
        )

        # List ALL objects in the bucket
        response = r2_client.list_objects_v2(Bucket='afrotc695recruitment')

        if 'Contents' not in response:
            print("No files found in bucket")
            return

        print(f"Found {len(response['Contents'])} total files in bucket:")
        print("-" * 80)

        # Sort by last modified (newest first)
        files = sorted(response['Contents'], key=lambda x: x.get('LastModified', datetime.min), reverse=True)

        backup_files = []
        other_files = []

        for obj in files:
            filename = obj['Key']
            size = obj.get('Size', 0)
            last_modified = obj.get('LastModified', None)

            if 'backup' in filename.lower() or filename.endswith('.json') or filename.endswith('.tar.gz'):
                backup_files.append((filename, size, last_modified))
            else:
                other_files.append((filename, size, last_modified))

        print("BACKUP FILES:")
        print("-" * 40)
        for filename, size, last_modified in backup_files:
            modified_str = last_modified.strftime('%Y-%m-%d %H:%M:%S') if last_modified else 'Unknown'
            print(f"{filename}")
            print(f"  Size: {size} bytes")
            print(f"  Modified: {modified_str}")
            print()

        print("OTHER FILES:")
        print("-" * 40)
        for filename, size, last_modified in other_files[:20]:  # Show first 20
            modified_str = last_modified.strftime('%Y-%m-%d %H:%M:%S') if last_modified else 'Unknown'
            print(f"{filename}")
            print(f"  Size: {size} bytes")
            print(f"  Modified: {modified_str}")
            print()

        if len(other_files) > 20:
            print(f"... and {len(other_files) - 20} more files")

    except Exception as e:
        print(f"Error checking R2 bucket: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


