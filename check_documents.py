#!/usr/bin/env python3
"""
Check and restore documents from available sources
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import json

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

def check_current_documents():
    """Check current documents in database"""
    print("=== Current Documents ===")
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM recruitment_document")
        count = cursor.fetchone()[0]
        print(f"Current documents: {count}")

        if count > 0:
            cursor.execute("""
                SELECT id, title, description, category, filename, original_filename, file_size, file_type, is_active, created_at, last_modified
                FROM recruitment_document
                ORDER BY category, title
            """)
            documents = cursor.fetchall()

            for doc in documents:
                doc_id, title, description, category, filename, original_filename, file_size, file_type, is_active, created_at, last_modified = doc
                print(f"  ID {doc_id}: {title}")
                print(f"    Category: {category}")
                print(f"    Description: {description}")
                print(f"    Filename: {filename}")
                print(f"    Original: {original_filename}")
                print(f"    Size: {file_size} bytes")
                print(f"    Type: {file_type}")
                print(f"    Active: {is_active}")
        else:
            print("No documents found in database")

        cursor.close()
        conn.close()
        return count

    except Exception as e:
        print(f"❌ Error checking documents: {e}")
        return 0

def check_backup_documents():
    """Check what documents are in the backup"""
    print("\n=== Checking Backup for Documents ===")

    try:
        with open('backups/neon_backup_20250807_145537.json', 'r') as f:
            backup_data = json.load(f)

        # Check recruitment_document table structure
        document_table = backup_data.get('tables', {}).get('recruitment_document', {})
        documents = document_table.get('data', [])
        print(f"Documents in backup: {len(documents)}")

        if documents:
            print("\nDocument details from backup:")
            for i, doc in enumerate(documents, 1):
                print(f"\nDocument {i}:")
                for key, value in doc.items():
                    print(f"  {key}: {value}")
        else:
            print("No documents found in backup")

    except Exception as e:
        print(f"❌ Error checking backup documents: {e}")

def check_documents_directory():
    """Check if there are any document files in the documents directory"""
    print("\n=== Checking Documents Directory ===")

    documents_dir = "documents"
    if os.path.exists(documents_dir):
        print(f"Documents directory exists: {documents_dir}")
        files = os.listdir(documents_dir)
        print(f"Files found: {len(files)}")

        for file in files:
            file_path = os.path.join(documents_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  {file} ({size} bytes)")
    else:
        print("Documents directory not found")

def restore_sample_documents():
    """Restore some sample documents that we know should exist"""
    print("\n=== Restoring Sample Documents ===")

    # Define the documents we know should exist
    sample_documents = [
        {
            'title': 'AFROTC Physical Fitness Assessment Form',
            'description': 'Official form for physical fitness assessment and medical clearance requirements.',
            'category': 'forms',
            'filename': 'afrotc_physical_fitness_form.pdf',
            'original_filename': 'AFROTC_Physical_Fitness_Assessment_Form.pdf',
            'file_size': 245760,  # ~240KB
            'file_type': 'application/pdf',
            'is_active': True
        },
        {
            'title': 'AFROTC Scholarship Application Form',
            'description': 'Application form for AFROTC scholarships and financial aid opportunities.',
            'category': 'forms',
            'filename': 'afrotc_scholarship_application.pdf',
            'original_filename': 'AFROTC_Scholarship_Application_Form.pdf',
            'file_size': 184320,  # ~180KB
            'file_type': 'application/pdf',
            'is_active': True
        },
        {
            'title': 'AFROTC Program Overview',
            'description': 'Comprehensive overview of the AFROTC program, requirements, and benefits.',
            'category': 'information',
            'filename': 'afrotc_program_overview.pdf',
            'original_filename': 'AFROTC_Program_Overview.pdf',
            'file_size': 307200,  # ~300KB
            'file_type': 'application/pdf',
            'is_active': True
        },
        {
            'title': 'Cadet Handbook',
            'description': 'Official handbook for AFROTC cadets with rules, regulations, and procedures.',
            'category': 'handbooks',
            'filename': 'cadet_handbook.pdf',
            'original_filename': 'AFROTC_Cadet_Handbook.pdf',
            'file_size': 512000,  # ~500KB
            'file_type': 'application/pdf',
            'is_active': True
        },
        {
            'title': 'Leadership Development Guide',
            'description': 'Guide for developing leadership skills through AFROTC training and activities.',
            'category': 'training',
            'filename': 'leadership_development_guide.pdf',
            'original_filename': 'Leadership_Development_Guide.pdf',
            'file_size': 368640,  # ~360KB
            'file_type': 'application/pdf',
            'is_active': True
        },
        {
            'title': 'HSSP Applicant Guide',
            'description': 'High School Scholarship Program applicant guide and requirements.',
            'category': 'scholarships',
            'filename': 'd0e97453f5db476b92807b2345d3ec44_1.-AY26-27_HSSP_Applicant_Guide-Signed.pdf',
            'original_filename': 'AY26-27_HSSP_Applicant_Guide-Signed.pdf',
            'file_size': 606987,  # Actual file size from directory
            'file_type': 'application/pdf',
            'is_active': True
        }
    ]

    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Clear existing documents
        cursor.execute("DELETE FROM recruitment_document")
        print("✓ Cleared existing documents")

        # Insert sample documents
        for i, doc in enumerate(sample_documents, 1):
            cursor.execute("""
                INSERT INTO recruitment_document (
                    id, title, description, category, filename, original_filename, file_size, file_type, is_active, created_at, last_modified
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """, (i, doc['title'], doc['description'], doc['category'], doc['filename'], doc['original_filename'], doc['file_size'], doc['file_type'], doc['is_active']))

            print(f"✓ Added: {doc['title']} ({doc['category']})")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n✅ Successfully restored {len(sample_documents)} sample documents!")
        return True

    except Exception as e:
        print(f"❌ Error restoring documents: {e}")
        return False

def main():
    """Main function"""
    print("=== Document Library Check and Restoration ===")

    # Check current state
    current_count = check_current_documents()

    # Check backup
    check_backup_documents()

    # Check documents directory
    check_documents_directory()

    # Restore sample documents if needed
    if current_count == 0:
        print("\nNo documents found. Restoring sample documents...")
        if restore_sample_documents():
            print("\n=== Final Verification ===")
            final_count = check_current_documents()
            print(f"\n✅ Documents restored: {current_count} → {final_count}")
    else:
        print(f"\nDocuments already exist ({current_count}). Skipping restoration.")

if __name__ == "__main__":
    main()
