#!/usr/bin/env python3
"""
Check the contents of the full backup tar.gz file
"""

import os
import json
import tarfile
import io
from dotenv import load_dotenv
from neon_backup_scheduler import get_r2_client

def main():
    load_dotenv()
    
    print("Checking contents of full backup file...")
    
    try:
        r2_client = get_r2_client()
        bucket_name = 'afrotc695recruitment'
        backup_filename = 'afrotc695_backup_full_20250825_065606.tar.gz'
        
        # Download the backup file
        print(f"Downloading {backup_filename}...")
        response = r2_client.get_object(Bucket=bucket_name, Key=backup_filename)
        backup_data = response['Body'].read()
        
        print(f"Downloaded {len(backup_data)} bytes")
        
        # Extract and examine the tar.gz file
        with tarfile.open(fileobj=io.BytesIO(backup_data), mode='r:gz') as tar:
            print("\nFiles in backup:")
            print("-" * 40)
            
            for member in tar.getmembers():
                print(f"{member.name} - {member.size} bytes")
                
                # If it's a JSON file, let's look at its contents
                if member.name.endswith('.json'):
                    print(f"  Reading {member.name}...")
                    f = tar.extractfile(member)
                    if f:
                        content = f.read().decode('utf-8')
                        try:
                            data = json.loads(content)
                            if 'tables' in data:
                                print(f"  Tables in backup:")
                                for table_name, records in data['tables'].items():
                                    print(f"    {table_name}: {len(records)} records")
                            elif 'description' in data:
                                print(f"  Description: {data['description']}")
                                print(f"  Created: {data.get('created_at', 'Unknown')}")
                        except json.JSONDecodeError:
                            print(f"  Not valid JSON")
                    print()
        
    except Exception as e:
        print(f"Error checking backup contents: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


