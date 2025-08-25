#!/usr/bin/env python3
"""
Add Local Documents to Database

This script adds the existing local documents to the database so they can be migrated to R2.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

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

def add_document_to_db(conn, title, filename, original_filename, file_size, file_type, category, description=""):
    """Add a document to the database"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recruitment_document
            (title, description, filename, original_filename, file_size, file_type, category, is_active, sort_order, created_at, last_modified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            title, description, filename, original_filename, file_size, file_type,
            category, True, 0, datetime.utcnow(), datetime.utcnow()
        ))
        document_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        print(f"   ✅ Added to database: {title} (ID: {document_id})")
        return document_id
    except Exception as e:
        print(f"   ❌ Error adding {title} to database: {e}")
        conn.rollback()
        return None

def main():
    """Main function to add local documents to database"""
    print("📄 Adding Local Documents to Database")
    print("=" * 50)

    # Check if documents folder exists
    documents_dir = Path("documents")
    if not documents_dir.exists():
        print("❌ Error: /documents folder not found")
        return False

    # Initialize database connection
    conn = get_database_connection()
    if not conn:
        return False

    try:
        # Document definitions
        documents = [
            {
                'filename': 'afrotc_physical_fitness_form.pdf',
                'title': 'AFROTC Physical Fitness Assessment Form',
                'description': 'Official AFROTC physical fitness assessment form for cadets',
                'category': 'forms'
            },
            {
                'filename': 'afrotc_scholarship_application.pdf',
                'title': 'AFROTC Scholarship Application Form',
                'description': 'Application form for AFROTC scholarships',
                'category': 'applications'
            },
            {
                'filename': 'cadet_handbook.pdf',
                'title': 'AFROTC Cadet Handbook',
                'description': 'Comprehensive handbook for AFROTC cadets',
                'category': 'guides'
            },
            {
                'filename': 'HSSP_Applicant_Guide-Signed.pdf',
                'title': 'HSSP Applicant Guide',
                'description': 'High School Scholarship Program applicant guide',
                'category': 'guides'
            },
            {
                'filename': 'leadership_development_guide.pdf',
                'title': 'Leadership Development Guide',
                'description': 'Guide for leadership development in AFROTC',
                'category': 'guides'
            }
        ]

        added_count = 0
        failed_count = 0

        for doc in documents:
            file_path = documents_dir / doc['filename']

            if not file_path.exists():
                print(f"⚠️  File not found: {doc['filename']}")
                failed_count += 1
                continue

            print(f"📄 Processing: {doc['title']}")

            # Get file size
            file_size = file_path.stat().st_size

            # Get file type
            file_type = file_path.suffix[1:] if file_path.suffix else 'pdf'

            # Add to database
            document_id = add_document_to_db(
                conn,
                doc['title'],
                doc['filename'],
                doc['filename'],
                file_size,
                file_type,
                doc['category'],
                doc['description']
            )

            if document_id:
                added_count += 1
            else:
                failed_count += 1

            print()

        print("=" * 50)
        print(f"✅ Database Update Complete!")
        print(f"   📊 Successfully added: {added_count}")
        print(f"   ❌ Failed additions: {failed_count}")

        return failed_count == 0

    except Exception as e:
        print(f"❌ Error during database update: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
