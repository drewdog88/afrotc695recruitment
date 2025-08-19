#!/usr/bin/env python3
"""
Test script to check the list_backup_files function
"""

from neon_backup_scheduler import list_backup_files

print("Testing list_backup_files function...")
try:
    files = list_backup_files()
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
