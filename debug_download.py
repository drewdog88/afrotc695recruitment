#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Debugging download process...")
print(f"BLOB_READ_WRITE_TOKEN: {'SET' if os.getenv('BLOB_READ_WRITE_TOKEN') else 'NOT SET'}")

try:
    from neon_backup_scheduler import download_backup_file

    # Test with a known backup file
    test_filename = "backups/afrotc695_backup_20250816_171633.json"

    print(f"Testing download of: {test_filename}")

    # Test the download function directly
    content = download_backup_file(test_filename)

    if content:
        print(f"✅ Direct download successful! Content length: {len(content)} bytes")
    else:
        print("❌ Direct download failed - no content returned")

    # Test the Flask wrapper function
    from app import download_backup_content

    flask_content = download_backup_content(test_filename)

    if flask_content:
        print(f"✅ Flask wrapper successful! Content length: {len(flask_content)} bytes")
    else:
        print("❌ Flask wrapper failed - no content returned")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
