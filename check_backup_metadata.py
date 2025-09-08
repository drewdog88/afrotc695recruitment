#!/usr/bin/env python3
"""
Check the metadata of the most recent full backup
"""

import os
import json
from dotenv import load_dotenv
from neon_backup_scheduler import get_r2_client

def main():
    load_dotenv()

    print("Checking most recent full backup metadata...")
    try:
        r2_client = get_r2_client()
        bucket_name = 'afrotc695recruitment'

        # Get the most recent full backup metadata
        response = r2_client.get_object(
            Bucket=bucket_name,
            Key='afrotc695_backup_full_20250825_065606.json'
        )

        metadata = json.loads(response['Body'].read().decode('utf-8'))

        print("Backup Metadata:")
        print(f"Timestamp: {metadata.get('timestamp')}")
        print(f"Backup Type: {metadata.get('backup_type')}")
        print(f"Description: {metadata.get('description')}")
        print(f"Database URL: {metadata.get('database_url', 'Not specified')}")
        print(f"File Size: {metadata.get('file_size')} bytes")
        print(f"Tables: {metadata.get('tables', [])}")
        print(f"Record Counts:")

        record_counts = metadata.get('record_counts', {})
        for table, count in record_counts.items():
            print(f"  {table}: {count}")

    except Exception as e:
        print(f"Error checking backup metadata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


