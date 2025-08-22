#!/usr/bin/env python3
"""
Test script for backup functions
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_backup_functions():
    """Test the backup functions"""
    print("Testing backup functions...")
    
    # Check environment variables
    print(f"CLOUDFLARE_R2_ACCESS_KEY_ID: {'SET' if os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID') else 'NOT SET'}")
    print(f"CLOUDFLARE_R2_ACCOUNT_ID: {'SET' if os.getenv('CLOUDFLARE_R2_ACCOUNT_ID') else 'NOT SET'}")
    print(f"CLOUDFLARE_R2_SECRET_ACCESS_KEY: {'SET' if os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY') else 'NOT SET'}")
    
    try:
        from neon_backup_scheduler import list_backup_files, backup_database_neon, create_full_backup_tgz
        
        print("\nTesting backup listing...")
        files = list_backup_files()
        print(f"Found {len(files)} backup files")
        
        if files:
            print("Sample files:")
            for f in files[:5]:
                print(f"  - {f['filename']} ({f['backup_type']})")
        
        print("\nTesting daily backup creation...")
        result = backup_database_neon("Test backup", "daily")
        print(f"Daily backup result: {result}")
        
        print("\nTesting full backup creation...")
        result = create_full_backup_tgz("Test full backup")
        print(f"Full backup result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backup_functions()
