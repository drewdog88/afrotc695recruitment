#!/usr/bin/env python3
"""
Test script to simulate accessing the database management page
"""

from app_local import app, get_backup_files

print("=== TESTING WEB BACKUP INTERFACE ===")

# Test within Flask app context
with app.app_context():
    print("1. Testing backup listing function...")
    backup_files = get_backup_files()
    print(f"Found {len(backup_files)} backup files")
    
    if backup_files:
        print("Sample backup files:")
        for i, backup in enumerate(backup_files[:3]):  # Show first 3
            print(f"  {i+1}. {backup['filename']} ({backup['size']} bytes)")
    
    print("\n2. Testing database management route simulation...")
    # Simulate what the route does
    try:
        # This is what the route does
        backup_files_for_template = get_backup_files()
        print(f"Route would pass {len(backup_files_for_template)} backup files to template")
        
        if backup_files_for_template:
            print("First backup file that would be shown:")
            first_backup = backup_files_for_template[0]
            print(f"  Filename: {first_backup['filename']}")
            print(f"  URL: {first_backup['url']}")
            print(f"  Size: {first_backup['size']} bytes")
            print(f"  Created: {first_backup['created']}")
        else:
            print("❌ No backup files found - this explains why the web page shows no backups!")
            
    except Exception as e:
        print(f"❌ Error in route simulation: {e}")

print("=== WEB TEST COMPLETE ===")
