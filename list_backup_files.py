#!/usr/bin/env python3
"""
List all backup files in Vercel Blob storage
"""

from neon_backup_scheduler import list_backup_files

def main():
    print("=== AFROTC 695 Backup Files in Vercel Blob ===")

    try:
        backup_files = list_backup_files()

        if not backup_files:
            print("❌ No backup files found")
            return

        print(f"📁 Found {len(backup_files)} backup files:")
        print()

        for i, backup in enumerate(backup_files, 1):
            print(f"{i}. {backup['filename']}")
            print(f"   Type: {backup['backup_type']}")
            print(f"   Size: {backup.get('size', 'Unknown')} bytes")
            print(f"   Created: {backup.get('created', 'Unknown')}")
            print(f"   Description: {backup.get('description', 'No description')}")
            print()

        print(f"Total: {len(backup_files)} backup files")

    except Exception as e:
        print(f"❌ Error listing backup files: {e}")

if __name__ == "__main__":
    main()

