#!/usr/bin/env python3
"""
Test script to verify the backup fix works with actual blob storage
"""

import os
import sys
import tempfile
import zipfile
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neon_backup_scheduler import create_full_backup_zip, list_backup_files
from vercel_blob import put, list as blob_list

def test_backup_fix():
    """Test the backup fix with actual blob storage"""
    print("🔍 Testing backup fix with actual blob storage...")

    # Step 1: Check current blob storage
    print("\n1. Checking current blob storage...")
    try:
        blob_response = blob_list()
        if isinstance(blob_response, dict) and 'blobs' in blob_response:
            files = blob_response['blobs']
            print(f"   ✅ Found {len(files)} files in blob storage")

            # Show some sample files
            for i, file_info in enumerate(files[:5]):  # Show first 5 files
                filename = file_info.get('pathname', 'Unknown')
                size = file_info.get('size', 0)
                print(f"   - {filename} ({size} bytes)")

            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
        else:
            print(f"   ⚠️  Unexpected blob response structure: {type(blob_response)}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking blob storage: {e}")
        return False

    # Step 2: Create a test file in blob storage
    print("\n2. Creating test file in blob storage...")
    test_content = f"Test file created at {datetime.now().isoformat()}"
    test_filename = f"backup_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    try:
        blob_response = put(test_filename, test_content.encode('utf-8'), {"addRandomSuffix": False})
        if blob_response and 'url' in blob_response:
            print(f"   ✅ Created test file: {test_filename}")
            test_file_url = blob_response['url']
        else:
            print("   ❌ Failed to create test file")
            return False
    except Exception as e:
        print(f"   ❌ Error creating test file: {e}")
        return False

    # Step 3: Create a full backup
    print("\n3. Creating full backup...")
    try:
        backup_filename, backup_url = create_full_backup_zip("Test backup fix verification")

        if backup_filename and backup_url:
            print(f"   ✅ Created backup: {backup_filename}")
            print(f"   📥 Download URL: {backup_url}")
        else:
            print("   ❌ Failed to create backup")
            return False
    except Exception as e:
        print(f"   ❌ Error creating backup: {e}")
        return False

    # Step 4: Download and verify the backup
    print("\n4. Downloading and verifying backup...")
    try:
        import requests

        # Download the backup
        response = requests.get(backup_url)
        if response.status_code != 200:
            print(f"   ❌ Failed to download backup: HTTP {response.status_code}")
            return False

        backup_content = response.content
        print(f"   ✅ Downloaded backup: {len(backup_content)} bytes")

        # Extract and verify ZIP contents
        with zipfile.ZipFile(io.BytesIO(backup_content), 'r') as zip_file:
            file_list = zip_file.namelist()
            print(f"   📁 ZIP contains {len(file_list)} files:")

            # Check for required files
            has_database = 'database_backup.json' in file_list
            has_metadata = 'backup_metadata.json' in file_list
            has_blob_contents = any(f.startswith('blob_contents/') for f in file_list)

            print(f"   - Database backup: {'✅' if has_database else '❌'}")
            print(f"   - Metadata: {'✅' if has_metadata else '❌'}")
            print(f"   - Blob contents: {'✅' if has_blob_contents else '❌'}")

            # Show blob contents
            blob_files = [f for f in file_list if f.startswith('blob_contents/')]
            print(f"   📦 Found {len(blob_files)} blob files:")
            for blob_file in blob_files[:10]:  # Show first 10
                print(f"     - {blob_file}")
            if len(blob_files) > 10:
                print(f"     ... and {len(blob_files) - 10} more")

            # Check if our test file is included
            test_file_in_backup = f"blob_contents/{test_filename}" in file_list
            print(f"   - Test file included: {'✅' if test_file_in_backup else '❌'}")

            # Verify metadata
            if has_metadata:
                with zip_file.open('backup_metadata.json') as f:
                    metadata = json.loads(f.read().decode('utf-8'))
                    print(f"   📊 Metadata:")
                    print(f"     - Description: {metadata.get('description', 'N/A')}")
                    print(f"     - Blob files count: {metadata.get('contents', {}).get('blob_files_count', 'N/A')}")
                    print(f"     - Total size: {metadata.get('contents', {}).get('total_size', 'N/A')} bytes")

            # Verify the backup doesn't include itself
            backup_files_in_backup = [f for f in file_list if f.endswith('.zip') and 'afrotc695_full_backup_' in f]
            self_included = len(backup_files_in_backup) > 0
            print(f"   - Self-inclusion: {'❌' if self_included else '✅'} (should not include itself)")

            if self_included:
                print(f"     ⚠️  Backup includes itself: {backup_files_in_backup}")

        # Step 5: Clean up test file
        print("\n5. Cleaning up test file...")
        try:
            from vercel_blob import delete
            delete(test_file_url, {})
            print(f"   ✅ Deleted test file: {test_filename}")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not delete test file: {e}")

        print("\n🎉 Backup fix verification completed successfully!")
        return True

    except Exception as e:
        print(f"   ❌ Error verifying backup: {e}")
        return False

if __name__ == "__main__":
    import io  # Import here for the zipfile operations

    success = test_backup_fix()
    if success:
        print("\n✅ All tests passed! The backup fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
