#!/usr/bin/env python3
"""
Document Migration Script: Local Documents to Cloudflare R2

This script migrates documents from the local /documents folder to Cloudflare R2 storage
and updates the database to point to the new R2 URLs.
"""

import os
import sys
import boto3
import uuid
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

# Load environment variables
load_dotenv()

# R2 Configuration
R2_ACCOUNT_ID = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.getenv('CLOUDFLARE_R2_BUCKET_NAME', 'afrotc695recruitment')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def get_r2_client():
    """Create and return R2 client"""
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        print("❌ Error: R2 credentials not configured")
        print("Please set: CLOUDFLARE_R2_ACCOUNT_ID, CLOUDFLARE_R2_ACCESS_KEY_ID, CLOUDFLARE_R2_SECRET_ACCESS_KEY")
        return None

    return boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )

def get_database_connection():
    """Create and return database connection"""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def upload_document_to_r2(r2_client, file_path, original_filename):
    """Upload a document to R2 and return the URL"""
    try:
        # Generate unique filename for R2
        file_extension = Path(original_filename).suffix
        unique_filename = f"documents/{uuid.uuid4().hex}_{original_filename}"

        # Upload to R2
        with open(file_path, 'rb') as file:
            r2_client.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=unique_filename,
                Body=file,
                ContentType='application/octet-stream'
            )

        # Generate public URL
        custom_domain = os.getenv('CLOUDFLARE_R2_CUSTOM_DOMAIN')
        if custom_domain:
            r2_url = f"https://{custom_domain}/{unique_filename}"
        else:
            r2_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{R2_BUCKET_NAME}/{unique_filename}"

        print(f"   ✅ Uploaded: {original_filename} → {r2_url}")
        return r2_url, unique_filename

    except Exception as e:
        print(f"   ❌ Error uploading {original_filename}: {e}")
        return None, None

def update_document_in_database(conn, document_id, r2_url, r2_filename):
    """Update document record in database with R2 URL"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE recruitment_document SET blob_url = %s, filename = %s, last_modified = %s WHERE id = %s",
            (r2_url, r2_filename, datetime.utcnow(), document_id)
        )
        conn.commit()
        cursor.close()
        print(f"   ✅ Updated database record for document ID {document_id}")
        return True
    except Exception as e:
        print(f"   ❌ Error updating database for document ID {document_id}: {e}")
        conn.rollback()
        return False

def get_existing_documents(conn):
    """Get all documents from database that don't have R2 URLs"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, filename, original_filename, blob_url
            FROM recruitment_document
            WHERE blob_url IS NULL OR blob_url = ''
            ORDER BY id
        """)
        documents = cursor.fetchall()
        cursor.close()
        return documents
    except Exception as e:
        print(f"❌ Error fetching documents from database: {e}")
        return []

def migrate_local_documents():
    """Migrate documents from local /documents folder to R2"""
    print("🚀 Starting Document Migration to Cloudflare R2")
    print("=" * 60)

    # Initialize R2 client
    r2_client = get_r2_client()
    if not r2_client:
        return False

    # Initialize database connection
    conn = get_database_connection()
    if not conn:
        return False

    try:
        # Get documents that need migration
        documents = get_existing_documents(conn)
        if not documents:
            print("✅ No documents found that need migration")
            return True

        print(f"📋 Found {len(documents)} documents to migrate")
        print()

        migrated_count = 0
        failed_count = 0

        for doc_id, title, filename, original_filename, blob_url in documents:
            print(f"📄 Processing: {title} (ID: {doc_id})")

            # Check if file exists in local documents folder
            local_file_path = Path("documents") / filename
            if not local_file_path.exists():
                print(f"   ⚠️  Local file not found: {local_file_path}")
                failed_count += 1
                continue

            # Upload to R2
            r2_url, r2_filename = upload_document_to_r2(r2_client, local_file_path, original_filename)
            if not r2_url:
                failed_count += 1
                continue

            # Update database
            if update_document_in_database(conn, doc_id, r2_url, r2_filename):
                migrated_count += 1
            else:
                failed_count += 1

            print()

        print("=" * 60)
        print(f"✅ Migration Complete!")
        print(f"   📊 Successfully migrated: {migrated_count}")
        print(f"   ❌ Failed migrations: {failed_count}")
        print(f"   📁 Documents now stored in R2 bucket: {R2_BUCKET_NAME}")

        return failed_count == 0

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    finally:
        conn.close()

def verify_migration():
    """Verify that all documents have R2 URLs"""
    print("\n🔍 Verifying Migration")
    print("=" * 30)

    conn = get_database_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, blob_url
            FROM recruitment_document
            ORDER BY id
        """)
        documents = cursor.fetchall()
        cursor.close()

        total_docs = len(documents)
        docs_with_r2 = sum(1 for _, _, blob_url in documents if blob_url and 'r2.cloudflarestorage.com' in blob_url)
        docs_without_r2 = total_docs - docs_with_r2

        print(f"📊 Total documents: {total_docs}")
        print(f"✅ Documents with R2 URLs: {docs_with_r2}")
        print(f"❌ Documents without R2 URLs: {docs_without_r2}")

        if docs_without_r2 > 0:
            print("\n⚠️  Documents still needing migration:")
            for doc_id, title, blob_url in documents:
                if not blob_url or 'r2.cloudflarestorage.com' not in blob_url:
                    print(f"   - {title} (ID: {doc_id})")

        return docs_without_r2 == 0

    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main migration function"""
    print("🇺🇸 AFROTC 695 Document Migration to Cloudflare R2")
    print("=" * 60)

    # Check prerequisites
    if not os.path.exists("documents"):
        print("❌ Error: /documents folder not found")
        return False

    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        print("❌ Error: R2 credentials not configured")
        print("Please set the following environment variables:")
        print("  - CLOUDFLARE_R2_ACCOUNT_ID")
        print("  - CLOUDFLARE_R2_ACCESS_KEY_ID")
        print("  - CLOUDFLARE_R2_SECRET_ACCESS_KEY")
        return False

    # Perform migration
    success = migrate_local_documents()

    if success:
        # Verify migration
        verify_migration()

        print("\n🎉 Migration completed successfully!")
        print("📝 Next steps:")
        print("   1. Test document downloads from the web interface")
        print("   2. Update the add_document route to use R2")
        print("   3. Remove local document storage code")
    else:
        print("\n❌ Migration failed. Please check the errors above.")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
