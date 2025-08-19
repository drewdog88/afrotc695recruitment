#!/usr/bin/env python3
"""
Check Vercel Blob storage structure
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
if os.path.exists("env.local"):
    load_dotenv()

try:
    from vercel_blob import list as blob_list

    print("Checking Vercel Blob storage structure...")
    response = blob_list()

    print("Blob list response type:", type(response))
    print("Blob list response:", response)

    # Handle different response formats
    if isinstance(response, dict) and 'blobs' in response:
        files = response['blobs']
    elif isinstance(response, list):
        files = response
    else:
        print(f"Unexpected response format: {type(response)}")
        files = []

    print(f"\nFound {len(files)} files in Vercel Blob storage:")
    print("-" * 80)

    backup_files = []
    other_files = []

    for f in files:
        if isinstance(f, dict):
            pathname = f.get('pathname', 'Unknown')
        else:
            pathname = str(f)

        if 'backup' in pathname.lower():
            backup_files.append(pathname)
        else:
            other_files.append(pathname)

    print("BACKUP FILES:")
    for path in sorted(backup_files):
        print(f"  {path}")

    print(f"\nOTHER FILES ({len(other_files)} total):")
    for path in sorted(other_files):
        print(f"  {path}")

except Exception as e:
    print(f"Error checking blob structure: {e}")
    import traceback
    traceback.print_exc()
