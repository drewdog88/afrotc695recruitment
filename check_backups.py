#!/usr/bin/env python3
"""
Check available backups
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
if os.path.exists("env.local"):
    load_dotenv("env.local")

try:
    from neon_backup_scheduler import list_backup_files

    print("Checking available backups...")
    files = list_backup_files()

    if not files:
        print("No backups found!")
    else:
        print(f"Found {len(files)} backup files:")
        print("-" * 80)
        for i, f in enumerate(files, 1):
            filename = f.get('filename', 'Unknown')
            backup_type = f.get('backup_type', 'Unknown')
            created = f.get('created', 'Unknown date')
            size = f.get('size', 0)

            print(f"{i:2d}. {filename}")
            print(f"    Type: {backup_type}")
            print(f"    Created: {created}")
            print(f"    Size: {size} bytes")
            print()

except Exception as e:
    print(f"Error checking backups: {e}")
    import traceback
    traceback.print_exc()
