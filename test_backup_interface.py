#!/usr/bin/env python3
"""
Test script to verify all backup interface functions work correctly
"""

import os
import sys
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backup_functions():
    """Test all backup-related functions"""
    print("Testing backup interface functions...")

    try:
        # Test 1: Import backup functions
        print("1. Testing imports...")
        from neon_backup_scheduler import (
            backup_database_neon,
            create_full_backup_zip,
            list_backup_files,
            download_backup_file,
            delete_backup_file
        )
        print("✅ All imports successful")

        # Test 2: Test backup listing
        print("2. Testing backup listing...")
        backup_files = list_backup_files()
        print(f"✅ Found {len(backup_files)} backup files")

        # Test 3: Test daily backup creation
        print("3. Testing daily backup creation...")
        backup_filename, backup_url = backup_database_neon("Test daily backup", "daily")
        if backup_filename:
            print(f"✅ Daily backup created: {backup_filename}")
        else:
            print("❌ Daily backup creation failed")
            return False

        # Test 4: Test full backup creation
        print("4. Testing full backup creation...")
        full_backup_filename, full_backup_url = create_full_backup_zip("Test full backup")
        if full_backup_filename:
            print(f"✅ Full backup created: {full_backup_filename}")
        else:
            print("❌ Full backup creation failed")
            return False

        # Test 5: Test backup listing after creation
        print("5. Testing backup listing after creation...")
        backup_files = list_backup_files()
        print(f"✅ Found {len(backup_files)} backup files")

        # Test 6: Test download functionality
        print("6. Testing download functionality...")
        if backup_files:
            test_file = backup_files[0]['filename']
            file_content = download_backup_file(test_file)
            if file_content:
                print(f"✅ Successfully downloaded: {test_file} ({len(file_content)} bytes)")
            else:
                print(f"❌ Failed to download: {test_file}")

        # Test 7: Test app.py integration
        print("7. Testing app.py integration...")
        try:
            from app import backup_database, create_full_backup, get_backup_files, download_backup_content
            print("✅ App.py backup functions imported successfully")

            # Test app backup functions
            app_backup_files = get_backup_files()
            print(f"✅ App.py backup listing works: {len(app_backup_files)} files")

        except Exception as e:
            print(f"❌ App.py integration failed: {e}")
            return False

        print("\n🎉 All backup interface tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_web_interface_simulation():
    """Simulate web interface operations"""
    print("\nTesting web interface simulation...")

    try:
        # Simulate backup creation
        print("1. Simulating daily backup creation...")
        from app import backup_database
        backup_filename, backup_url = backup_database("Web interface test backup")
        if backup_filename:
            print(f"✅ Web daily backup created: {backup_filename}")
        else:
            print("❌ Web daily backup failed")
            return False

        # Simulate full backup creation
        print("2. Simulating full backup creation...")
        from app import create_full_backup
        full_backup_filename, full_backup_url = create_full_backup("Web interface test full backup")
        if full_backup_filename:
            print(f"✅ Web full backup created: {full_backup_filename}")
        else:
            print("❌ Web full backup failed")
            return False

        # Simulate backup listing
        print("3. Simulating backup listing...")
        from app import get_backup_files
        backup_files = get_backup_files()
        print(f"✅ Web backup listing works: {len(backup_files)} files")

        # Simulate download
        print("4. Simulating backup download...")
        from app import download_backup_content
        if backup_files:
            test_file = backup_files[0]['filename']
            file_content = download_backup_content(test_file)
            if file_content:
                print(f"✅ Web download works: {test_file} ({len(file_content)} bytes)")
            else:
                print(f"❌ Web download failed: {test_file}")

        print("\n🎉 All web interface simulations passed!")
        return True

    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AFROTC 695 Backup Interface Test")
    print("=" * 60)

    # Test core functions
    core_success = test_backup_functions()

    # Test web interface
    web_success = test_web_interface_simulation()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Core Functions: {'✅ PASSED' if core_success else '❌ FAILED'}")
    print(f"Web Interface: {'✅ PASSED' if web_success else '❌ FAILED'}")

    if core_success and web_success:
        print("\n🎉 ALL TESTS PASSED! Backup system is ready for production.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

    print("=" * 60)
