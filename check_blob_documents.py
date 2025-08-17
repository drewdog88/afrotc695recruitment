#!/usr/bin/env python3
"""
Check what documents exist in Vercel Blob storage
"""

import os
import sys
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

def check_blob_storage():
    """Check what documents exist in Vercel Blob storage"""
    print("=== Checking Vercel Blob Storage for Documents ===")

    blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
    if not blob_token:
        print("❌ Error: BLOB_READ_WRITE_TOKEN not found in environment variables")
        return False

    try:
        # List all blobs
        url = "https://blob.vercel-storage.com"
        headers = {
            'Authorization': f'Bearer {blob_token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            blobs_data = response.json()
            print(f"Raw response: {blobs_data}")

            # Handle different response formats
            if isinstance(blobs_data, dict) and 'blobs' in blobs_data:
                blobs = blobs_data['blobs']
            elif isinstance(blobs_data, list):
                blobs = blobs_data
            else:
                print(f"Unexpected response format: {type(blobs_data)}")
                return False

            print(f"Found {len(blobs)} blobs in storage")

            # Filter for documents
            documents = []
            for blob in blobs:
                if isinstance(blob, dict):
                    pathname = blob.get('pathname', '')
                    if any(ext in pathname.lower() for ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt']):
                        documents.append(blob)
                else:
                    print(f"Unexpected blob format: {blob}")

            print(f"\nFound {len(documents)} document files:")
            for doc in documents:
                print(f"  {doc.get('pathname', 'Unknown')}")
                print(f"    URL: {doc.get('url', 'No URL')}")
                print(f"    Size: {doc.get('size', 'Unknown')} bytes")
                print(f"    Uploaded: {doc.get('uploadedAt', 'Unknown')}")
                print()

            return documents
        else:
            print(f"❌ Error accessing blob storage: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error checking blob storage: {e}")
        return False

def check_local_documents():
    """Check what documents exist locally"""
    print("\n=== Checking Local Documents Directory ===")

    documents_dir = "documents"
    if os.path.exists(documents_dir):
        files = os.listdir(documents_dir)
        print(f"Found {len(files)} files in local documents directory:")

        for file in files:
            file_path = os.path.join(documents_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  {file} ({size} bytes)")
    else:
        print("Local documents directory not found")

def main():
    """Main function"""
    print("=== Document Storage Analysis ===")

    # Check blob storage
    blob_docs = check_blob_storage()

    # Check local documents
    check_local_documents()

    if blob_docs:
        print(f"\n✅ Found {len(blob_docs)} documents in Vercel Blob storage")
        print("These documents can be accessed via their URLs and should be referenced in the database.")
    else:
        print("\n⚠ No documents found in Vercel Blob storage")
        print("Documents may be stored locally or need to be uploaded to blob storage.")

if __name__ == "__main__":
    main()
