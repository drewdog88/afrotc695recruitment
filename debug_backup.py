#!/usr/bin/env python3
"""
Debug script to test backup functionality within Flask app context
"""

from app_local import app, get_backup_files, backup_database

print("=== DEBUGGING BACKUP SYSTEM ===")

# Test within Flask app context
with app.app_context():
    print("1. Testing backup listing...")
    backup_files = get_backup_files()
    print(f"Found {len(backup_files)} backup files")
    
    if backup_files:
        print("First backup file:")
        print(f"  Filename: {backup_files[0]['filename']}")
        print(f"  URL: {backup_files[0]['url']}")
        print(f"  Size: {backup_files[0]['size']} bytes")
        print(f"  Created: {backup_files[0]['created']}")
    
    print("\n2. Testing backup creation...")
    try:
        result = backup_database("Debug test backup")
        if result and result[0]:
            print(f"✅ Backup created successfully: {result[0]}")
            print(f"   URL: {result[1]}")
        else:
            print("❌ Backup creation failed")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
    
    print("\n3. Testing backup listing again...")
    backup_files_after = get_backup_files()
    print(f"Found {len(backup_files_after)} backup files after creation")

print("=== DEBUG COMPLETE ===")
