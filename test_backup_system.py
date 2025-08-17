#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env.local')

print("Testing backup system...")
print(f"BLOB_READ_WRITE_TOKEN: {'SET' if os.getenv('BLOB_READ_WRITE_TOKEN') else 'NOT SET'}")

try:
    from neon_backup_scheduler import list_backup_files
    files = list_backup_files()
    print(f"Found {len(files)} backup files")

    # Show the structure of the first file
    if files:
        print("\nFirst file structure:")
        for key, value in files[0].items():
            print(f"  {key}: {value}")

    print("\nAll files:")
    for i, file in enumerate(files[:5]):
        print(f"{i+1}. {file.get('filename', 'NO_FILENAME')} - Size: {file.get('size', 'NO_SIZE')}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
