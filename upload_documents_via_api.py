#!/usr/bin/env python3
"""
Script to upload documents using the proper web API instead of direct database manipulation
"""

import requests
import os
from pathlib import Path

def upload_document_via_api(file_path, title, description, category='general'):
    """Upload a document using the web API"""

    # You'll need to be logged in as admin to use this
    # This is a simulation - in practice, you'd need to:
    # 1. Login to get session cookies
    # 2. Use those cookies to make the upload request

    print(f"📄 Would upload: {title}")
    print(f"   File: {file_path}")
    print(f"   Description: {description}")
    print(f"   Category: {category}")
    print("   ⚠️  This requires admin login and session management")

    # For now, let's just show what would be uploaded
    if file_path.exists():
        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
        print(f"   📊 File size: {file_size:.2f}MB")
        return True
    else:
        print(f"   ❌ File not found: {file_path}")
        return False

def main():
    """Main upload process"""
    print("🚀 Document Upload via Web API")
    print("=" * 50)

    # Documents to upload
    documents_to_upload = [
        {
            'file_path': Path('documents/AFROTC Handout.pdf'),
            'title': 'AFROTC Handout',
            'description': 'Comprehensive AFROTC program information and requirements',
            'category': 'general'
        },
        {
            'file_path': Path('documents/Medical Programs.pptx'),
            'title': 'Medical Programs',
            'description': 'Information about Air Force medical programs and opportunities',
            'category': 'programs'
        },
        {
            'file_path': Path('documents/USAF Pilot Training Pipeline.pdf'),
            'title': 'USAF Pilot Training Pipeline',
            'description': 'Complete guide to USAF pilot training pipeline and requirements',
            'category': 'programs'
        }
    ]

    print("\n📋 Documents to upload:")
    for i, doc in enumerate(documents_to_upload, 1):
        print(f"{i}. {doc['title']}")

    print("\n🔧 Manual Upload Instructions:")
    print("1. Go to https://afrotc695recruitment.vercel.app/materials")
    print("2. Click 'Upload Document' button")
    print("3. Fill in the form for each document:")

    for doc in documents_to_upload:
        print(f"\n   📄 {doc['title']}:")
        print(f"      Title: {doc['title']}")
        print(f"      Description: {doc['description']}")
        print(f"      Category: {doc['category']}")
        print(f"      File: {doc['file_path']}")

    print("\n✅ After uploading, the documents will be available in the document library!")

if __name__ == "__main__":
    main()
