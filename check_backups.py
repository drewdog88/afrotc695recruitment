#!/usr/bin/env python3
"""
Check available backup files in blob storage
"""

from api.app import get_backup_files

def main():
    print("🔍 Checking available backup files...")
    
    try:
        backup_files = get_backup_files()
        
        if not backup_files:
            print("❌ No backup files found in blob storage")
            return
        
        print(f"✅ Found {len(backup_files)} backup files:")
        for i, backup in enumerate(backup_files, 1):
            print(f"  {i}. {backup['filename']}")
            print(f"     Size: {backup['size']} bytes")
            print(f"     Uploaded: {backup['uploadedAt']}")
            print(f"     URL: {backup['url']}")
            print()
            
    except Exception as e:
        print(f"❌ Error checking backup files: {e}")

if __name__ == "__main__":
    main()
