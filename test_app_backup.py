#!/usr/bin/env python3
"""
Test script to check the Flask app's get_backup_files function
"""

from app import get_backup_files

print("Testing Flask app get_backup_files function...")
try:
    files = get_backup_files()
    print(f"Found {len(files)} backup files")

    if files:
        print("\nFirst 5 backup files:")
        for i, f in enumerate(files[:5]):
            print(f"{i+1}. {f['filename']} ({f['backup_type']}) - {f.get('size', 0)} bytes")
    else:
        print("No backup files found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
