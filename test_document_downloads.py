#!/usr/bin/env python3
"""
Test Document Downloads

This script tests that document downloads are working correctly with the new R2 URLs.
"""

import os
import sys
import requests
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def get_database_connection():
    """Create and return database connection"""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def test_document_downloads():
    """Test document downloads from R2 using presigned URLs"""
    print("🔍 Testing Document Downloads (Presigned URLs)")
    print("=" * 50)

    # Import R2 utilities
    try:
        from utils.r2_document_utils import generate_presigned_url, is_r2_configured
    except ImportError:
        print("❌ R2 utilities not available")
        return False

    # Check if R2 is configured
    if not is_r2_configured():
        print("❌ R2 not configured")
        return False

    # Initialize database connection
    conn = get_database_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, filename, original_filename, blob_url
            FROM recruitment_document
            WHERE blob_url IS NOT NULL AND blob_url != '' AND filename IS NOT NULL
            ORDER BY id
        """)
        documents = cursor.fetchall()
        cursor.close()

        if not documents:
            print("❌ No documents found with R2 URLs")
            return False

        print(f"📋 Found {len(documents)} documents to test")
        print()

        success_count = 0
        failed_count = 0

        for doc_id, title, filename, original_filename, blob_url in documents:
            print(f"📄 Testing: {title}")
            print(f"   R2 Filename: {filename}")

            try:
                # Generate presigned URL
                presigned_url = generate_presigned_url(filename, expiration=300)  # 5 minutes
                if not presigned_url:
                    print(f"   ❌ Failed to generate presigned URL")
                    failed_count += 1
                    continue

                print(f"   Presigned URL: {presigned_url[:80]}...")

                # Test the download
                response = requests.get(presigned_url, timeout=30)

                if response.status_code == 200:
                    content_length = len(response.content)
                    print(f"   ✅ Download successful: {content_length} bytes")
                    success_count += 1
                else:
                    print(f"   ❌ Download failed: HTTP {response.status_code}")
                    failed_count += 1

            except Exception as e:
                print(f"   ❌ Download error: {e}")
                failed_count += 1

            print()

        print("=" * 50)
        print(f"📊 Test Results:")
        print(f"   ✅ Successful downloads: {success_count}")
        print(f"   ❌ Failed downloads: {failed_count}")

        if failed_count == 0:
            print("🎉 All document downloads are working correctly!")
        else:
            print("⚠️  Some document downloads failed. Please check the R2 configuration.")

        return failed_count == 0

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main test function"""
    print("🇺🇸 AFROTC 695 Document Download Test")
    print("=" * 50)

    success = test_document_downloads()

    if success:
        print("\n✅ All tests passed! Document system is ready.")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
