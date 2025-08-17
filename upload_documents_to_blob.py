#!/usr/bin/env python3
"""
Upload existing local documents to Vercel Blob storage and update database
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import requests
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get connection to production database"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        sys.exit(1)

    # Convert postgres:// to postgresql:// for psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def upload_file_to_blob(file_path, filename):
    """Upload a file to Vercel Blob storage"""
    blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
    if not blob_token:
        print("❌ Error: BLOB_READ_WRITE_TOKEN not found in environment variables")
        return None

    try:
        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Generate a unique blob pathname
        blob_pathname = f"documents/{uuid.uuid4().hex}_{filename}"

        # Upload to Vercel Blob using PUT method
        url = f"https://blob.vercel-storage.com/{blob_pathname}"
        headers = {
            'Authorization': f'Bearer {blob_token}',
            'Content-Type': 'application/octet-stream'
        }

        response = requests.put(
            url,
            data=file_data,
            headers=headers,
            params={
                'addRandomSuffix': 'false'
            }
        )

        if response.status_code in [200, 201]:
            blob_response = response.json()
            if 'url' in blob_response:
                print(f"✓ Uploaded {filename} to blob storage")
                return blob_response['url']
            else:
                print(f"❌ Upload failed for {filename}: No URL in response")
                return None
        else:
            print(f"❌ Upload failed for {filename}: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error uploading {filename}: {e}")
        return None

def update_document_blob_url(conn, document_id, blob_url):
    """Update document record with blob URL"""
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE recruitment_document
            SET blob_url = %s, last_modified = NOW()
            WHERE id = %s
        """, (blob_url, document_id))

        conn.commit()
        print(f"✓ Updated document ID {document_id} with blob URL")
        return True

    except Exception as e:
        print(f"❌ Error updating document {document_id}: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def upload_local_documents():
    """Upload local documents to blob storage and update database"""
    print("=== Uploading Local Documents to Vercel Blob Storage ===")

    conn = get_database_connection()

    # Check local documents directory
    documents_dir = "documents"
    if not os.path.exists(documents_dir):
        print("❌ Local documents directory not found")
        return False

    local_files = os.listdir(documents_dir)
    print(f"Found {len(local_files)} files in local documents directory")

    # Get current documents from database
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, filename, original_filename, blob_url
        FROM recruitment_document
        ORDER BY id
    """)
    db_documents = cursor.fetchall()
    cursor.close()

    print(f"Found {len(db_documents)} documents in database")

    # Upload each local file and update database
    for doc in db_documents:
        doc_id, title, filename, original_filename, blob_url = doc

        # Skip if already has blob URL
        if blob_url:
            print(f"⚠ Document '{title}' already has blob URL, skipping")
            continue

        # Check if local file exists
        local_file_path = os.path.join(documents_dir, filename)
        if not os.path.exists(local_file_path):
            print(f"⚠ Local file for '{title}' not found: {local_file_path}")
            continue

        # Upload to blob storage
        print(f"\nUploading '{title}' ({original_filename})...")
        blob_url = upload_file_to_blob(local_file_path, original_filename)

        if blob_url:
            # Update database
            if update_document_blob_url(conn, doc_id, blob_url):
                print(f"✅ Successfully uploaded and updated '{title}'")
            else:
                print(f"❌ Failed to update database for '{title}'")
        else:
            print(f"❌ Failed to upload '{title}' to blob storage")

    conn.close()
    print("\n=== Document upload complete ===")

def verify_blob_urls():
    """Verify that documents have blob URLs"""
    print("\n=== Verifying Blob URLs ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, filename, blob_url
        FROM recruitment_document
        ORDER BY id
    """)

    documents = cursor.fetchall()

    print(f"Document blob URL status:")
    for doc in documents:
        doc_id, title, filename, blob_url = doc
        status = "✅ Has blob URL" if blob_url else "❌ No blob URL"
        print(f"  {doc_id}: {title} - {status}")
        if blob_url:
            print(f"    URL: {blob_url}")

    cursor.close()
    conn.close()

def main():
    """Main function"""
    print("=== Document Migration to Vercel Blob Storage ===")

    # Upload local documents to blob storage
    upload_local_documents()

    # Verify the results
    verify_blob_urls()

    print("\n✅ Document migration complete!")
    print("Documents are now stored in Vercel Blob storage with URLs tracked in the database.")

if __name__ == "__main__":
    main()
