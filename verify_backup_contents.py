#!/usr/bin/env python3
"""
Verify backup contents to ensure Vercel Blob files are included
"""

import tarfile
import io
import json
from dotenv import load_dotenv
from neon_backup_scheduler import download_backup_file_r2

def verify_backup_contents(backup_filename):
    """Verify the contents of a backup file"""
    print(f"=== Verifying Backup: {backup_filename} ===")
    
    # Download backup
    content = download_backup_file_r2(backup_filename)
    if not content:
        print("❌ Failed to download backup")
        return
    
    print(f"Downloaded {len(content)} bytes")
    
    # Extract and analyze
    tar = tarfile.open(fileobj=io.BytesIO(content), mode='r:gz')
    
    print("\n📁 Files in backup:")
    vercel_blob_files = []
    r2_backup_files = []
    other_files = []
    
    for member in tar.getmembers():
        if member.name.startswith('vercel_blob_files/'):
            vercel_blob_files.append(member)
        elif member.name.startswith('r2_backup_files/'):
            r2_backup_files.append(member)
        else:
            other_files.append(member)
    
    print(f"\n📄 Vercel Blob files ({len(vercel_blob_files)}):")
    for member in vercel_blob_files:
        print(f"  {member.name} ({member.size} bytes)")
    
    print(f"\n💾 R2 Backup files ({len(r2_backup_files)}):")
    for member in r2_backup_files[:5]:  # Show first 5
        print(f"  {member.name} ({member.size} bytes)")
    if len(r2_backup_files) > 5:
        print(f"  ... and {len(r2_backup_files) - 5} more")
    
    print(f"\n📋 Other files ({len(other_files)}):")
    for member in other_files:
        print(f"  {member.name} ({member.size} bytes)")
    
    # Extract and verify metadata
    try:
        metadata_file = tar.extractfile('backup_metadata.json')
        metadata = json.loads(metadata_file.read().decode('utf-8'))
        
        print(f"\n📊 Backup Summary:")
        print(f"  Description: {metadata.get('description', 'N/A')}")
        print(f"  Created: {metadata.get('created_at', 'N/A')}")
        print(f"  Total size: {metadata.get('contents', {}).get('total_size', 0)} bytes")
        print(f"  Vercel Blob files: {metadata.get('contents', {}).get('vercel_blob_files_count', 0)}")
        print(f"  R2 Backup files: {metadata.get('contents', {}).get('r2_backup_files_count', 0)}")
        
        # Verify Vercel Blob files match metadata
        vercel_files_metadata = metadata.get('contents', {}).get('vercel_blob_files', [])
        if len(vercel_blob_files) == len(vercel_files_metadata):
            print("✅ Vercel Blob file count matches metadata")
        else:
            print(f"❌ Vercel Blob file count mismatch: {len(vercel_blob_files)} vs {len(vercel_files_metadata)}")
            
    except Exception as e:
        print(f"❌ Error reading metadata: {e}")
    
    tar.close()
    print("\n🎉 Backup verification completed!")

if __name__ == "__main__":
    load_dotenv()
    verify_backup_contents('afrotc695_backup_full_20250824_111447.tar.gz')
