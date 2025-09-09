#!/usr/bin/env python3
"""
Script to upload new documents from local /documents folder to Cloudflare R2
and add them to the database
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from app import app, db, RecruitmentDocument
from utils.r2_document_utils import upload_document_to_r2, validate_file_type, get_file_size_mb, is_r2_configured

load_dotenv()

def upload_new_documents():
    """Upload new documents from local documents folder"""
    if not is_r2_configured():
        print("❌ R2 not configured properly")
        return

    # Documents to upload (excluding ones already in system)
    new_documents = [
        {
            'filename': 'AFROTC Handout.pdf',
            'title': 'AFROTC Handout',
            'description': 'Comprehensive AFROTC program information and requirements',
            'category': 'general'
        },
        {
            'filename': 'Air Force ROTC Fact Sheet.pub',
            'title': 'Air Force ROTC Fact Sheet',
            'description': 'Official Air Force ROTC fact sheet with key information',
            'category': 'general'
        },
        {
            'filename': 'Medical Programs.pptx',
            'title': 'Medical Programs',
            'description': 'Information about Air Force medical programs and opportunities',
            'category': 'programs'
        },
        {
            'filename': 'USAF Pilot Training Pipeline.pdf',
            'title': 'USAF Pilot Training Pipeline',
            'description': 'Complete guide to USAF pilot training pipeline and requirements',
            'category': 'programs'
        }
    ]

    documents_folder = Path('documents')

    with app.app_context():
        for doc_info in new_documents:
            file_path = documents_folder / doc_info['filename']

            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                continue

            print(f"\n📄 Processing: {doc_info['title']}")
            print(f"   File: {file_path}")

            # Validate file type
            if not validate_file_type(doc_info['filename']):
                print(f"   ❌ Invalid file type: {doc_info['filename']}")
                continue

            # Check file size
            file_size_mb = get_file_size_mb(open(file_path, 'rb'))
            if file_size_mb > 10.0:  # 10MB limit
                print(f"   ❌ File too large: {file_size_mb:.2f}MB (max 10MB)")
                continue

            print(f"   📊 File size: {file_size_mb:.2f}MB")

            try:
                # Upload to R2
                with open(file_path, 'rb') as f:
                    from werkzeug.datastructures import FileStorage
                    file_storage = FileStorage(f, filename=doc_info['filename'])

                    r2_url, r2_filename, error = upload_document_to_r2(file_storage, doc_info['filename'])

                    if error:
                        print(f"   ❌ Upload failed: {error}")
                        continue

                    print(f"   ✅ Uploaded to R2: {r2_filename}")
                    print(f"   🔗 R2 URL: {r2_url}")

                # Add to database
                document = RecruitmentDocument(
                    title=doc_info['title'],
                    description=doc_info['description'],
                    filename=r2_filename,
                    original_filename=doc_info['filename'],
                    file_size=int(file_size_mb * 1024 * 1024),  # Convert to bytes
                    file_type=Path(doc_info['filename']).suffix[1:],  # Remove the dot
                    category=doc_info['category'],
                    blob_url=r2_url,
                    is_active=True,
                    sort_order=0
                )

                db.session.add(document)
                db.session.commit()

                print(f"   ✅ Added to database with ID: {document.id}")

            except Exception as e:
                print(f"   ❌ Error processing {doc_info['filename']}: {e}")
                db.session.rollback()
                continue

def replace_program_overview():
    """Replace AFROTC Program Overview with AFROTC Handout"""
    with app.app_context():
        # Find the AFROTC Program Overview document
        program_overview = RecruitmentDocument.query.filter_by(
            title='AFROTC Program Overview'
        ).first()

        if program_overview:
            print(f"\n🔄 Replacing AFROTC Program Overview with AFROTC Handout")
            print(f"   Current title: {program_overview.title}")

            # Update the title and description
            program_overview.title = 'AFROTC Handout'
            program_overview.description = 'Comprehensive AFROTC program information and requirements'
            program_overview.category = 'general'

            db.session.commit()
            print(f"   ✅ Updated to: {program_overview.title}")
        else:
            print(f"\n⚠️  AFROTC Program Overview not found in database")

if __name__ == "__main__":
    print("🚀 Starting document upload process...")
    upload_new_documents()
    replace_program_overview()
    print("🏁 Upload process completed")
