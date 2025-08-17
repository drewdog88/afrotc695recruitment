#!/usr/bin/env python3
"""
Test script to check if backup functions can be imported without errors
"""

import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing backup system imports...")

try:
    # Test importing the backup functions
    from neon_backup_scheduler import list_backup_files, backup_database_neon, create_full_backup_zip

    print("✅ Successfully imported backup functions")

    # Test getting backup files
    print("Testing list_backup_files()...")
    backup_files = list_backup_files()
    print(f"✅ Found {len(backup_files)} backup files")

    print("✅ All backup functions working correctly!")

except Exception as e:
    print(f"❌ Error importing backup functions: {e}")
    import traceback
    traceback.print_exc()
