#!/usr/bin/env python3
"""
Verify we're using the correct blob store
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
if os.path.exists("env.local"):
    load_dotenv()

print("Environment check:")
print(f"BLOB_READ_WRITE_TOKEN: {os.getenv('BLOB_READ_WRITE_TOKEN')}")

try:
    from vercel_blob import list as blob_list

    print("\nTesting blob connection...")
    response = blob_list()

    if isinstance(response, dict) and 'blobs' in response:
        files = response['blobs']
    else:
        files = response if isinstance(response, list) else []

    print(f"Connected successfully! Found {len(files)} files.")

    if files:
        # Check the URL of the first file to verify store
        first_file = files[0]
        if isinstance(first_file, dict) and 'url' in first_file:
            url = first_file['url']
            print(f"Sample file URL: {url}")

            if 'pwmalcxzcqu5etro' in url.lower():
                print("✅ CORRECT STORE: Using store_pWMALcxzCqU5EtRO (Production)")
            elif 'kre9xoivjggj03of' in url.lower():
                print("❌ WRONG STORE: Using store_kRe9XoIvjggJ03oF")
            else:
                print(f"⚠️  UNKNOWN STORE: {url}")

        # Show a few backup files
        backup_files = [f for f in files if isinstance(f, dict) and 'backup' in f.get('pathname', '').lower()]
        print(f"\nFound {len(backup_files)} backup files:")
        for i, f in enumerate(backup_files[:5]):
            print(f"  {i+1}. {f.get('pathname', 'Unknown')}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
