#!/usr/bin/env python3
"""Get latest backup info from R2"""

from dotenv import load_dotenv
from neon_backup_scheduler import list_backup_files

load_dotenv()

def get_latest_backup():
    backups = list_backup_files()
    full_backups = [b for b in backups if b.get('backup_type') == 'full' and b.get('size', 0) > 50000]

    if not full_backups:
        print("No large full backups found")
        return None

    latest = max(full_backups, key=lambda x: x.get('created'))
    print(f"Latest full backup: {latest['filename']}")
    print(f"Size: {latest['size']} bytes")
    print(f"Created: {latest['created']}")
    print(f"Description: {latest.get('description', 'N/A')}")

    return latest

if __name__ == "__main__":
    get_latest_backup()
