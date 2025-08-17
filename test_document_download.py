#!/usr/bin/env python3
"""
Test document download functionality with blob URLs
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import requests

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

def test_blob_urls():
    """Test that blob URLs are accessible"""
    print("=== Testing Blob URL Accessibility ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, blob_url
        FROM recruitment_document
        WHERE blob_url IS NOT NULL
        ORDER BY id
    """)

    documents = cursor.fetchall()

    print(f"Testing {len(documents)} documents with blob URLs:")

    for doc in documents:
        doc_id, title, blob_url = doc
        print(f"\nTesting document {doc_id}: {title}")
        print(f"  Blob URL: {blob_url}")

        try:
            # Test the blob URL
            response = requests.head(blob_url, timeout=10)

            if response.status_code == 200:
                print(f"  ✅ URL accessible (Status: {response.status_code})")
                print(f"  Content-Type: {response.headers.get('content-type', 'Unknown')}")
                print(f"  Content-Length: {response.headers.get('content-length', 'Unknown')} bytes")
            else:
                print(f"  ❌ URL not accessible (Status: {response.status_code})")

        except Exception as e:
            print(f"  ❌ Error testing URL: {e}")

    cursor.close()
    conn.close()

def test_document_metadata():
    """Test document metadata in database"""
    print("\n=== Document Metadata in Database ===")

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, filename, original_filename, file_size, file_type, blob_url
        FROM recruitment_document
        ORDER BY id
    """)

    documents = cursor.fetchall()

    print(f"Document metadata:")
    for doc in documents:
        doc_id, title, filename, original_filename, file_size, file_type, blob_url = doc
        print(f"\n  Document {doc_id}: {title}")
        print(f"    Filename: {filename}")
        print(f"    Original: {original_filename}")
        print(f"    Size: {file_size} bytes")
        print(f"    Type: {file_type}")
        print(f"    Has Blob URL: {'✅ Yes' if blob_url else '❌ No'}")
        if blob_url:
            print(f"    Blob URL: {blob_url[:80]}...")

    cursor.close()
    conn.close()

def main():
    """Main test function"""
    print("=== Document Download Test ===")

    # Test blob URL accessibility
    test_blob_urls()

    # Test document metadata
    test_document_metadata()

    print("\n✅ Document download test complete!")
    print("All documents should now be accessible via their blob URLs.")

if __name__ == "__main__":
    main()
