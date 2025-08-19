#!/usr/bin/env python3
"""
Test script to check environment variables in Flask app context
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment variable check:")
print(f"BLOB_READ_WRITE_TOKEN: {'SET' if os.getenv('BLOB_READ_WRITE_TOKEN') else 'NOT SET'}")
print(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")

# Test the Flask app's get_backup_files function
from app import get_backup_files

print("\nTesting Flask app get_backup_files function...")
try:
    files = get_backup_files()
    print(f"Found {len(files)} backup files")

    if files:
        print("Backup files found - function working correctly")
    else:
        print("No backup files found - this might be the issue")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
