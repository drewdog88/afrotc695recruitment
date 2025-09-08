#!/usr/bin/env python3
"""
Test script to verify the document download route logic
"""

import os
from dotenv import load_dotenv
from app import app, db, RecruitmentDocument
from utils.r2_document_utils import generate_presigned_url, is_r2_configured

load_dotenv()

def test_download_logic():
    """Test the download route logic"""
    with app.app_context():
        if not is_r2_configured():
            print("❌ R2 not configured")
            return
        
        docs = RecruitmentDocument.query.filter(
            RecruitmentDocument.blob_url.isnot(None),
            RecruitmentDocument.blob_url != ''
        ).all()
        
        print(f"🧪 Testing download logic for {len(docs)} documents...")
        
        for doc in docs:
            print(f"\n📄 Testing: {doc.title}")
            print(f"   Blob URL: {doc.blob_url}")
            
            # Simulate the download route logic
            if doc.filename and doc.blob_url and 'r2.cloudflarestorage.com' in doc.blob_url:
                # Extract R2 key from blob_url
                bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME', 'afrotc695recruitment')
                url_parts = doc.blob_url.split(f'/{bucket_name}/')
                if len(url_parts) > 1:
                    r2_key = url_parts[1]
                else:
                    r2_key = doc.blob_url.split('/')[-1]
                
                print(f"   Extracted R2 key: {r2_key}")
                
                # Generate presigned URL
                presigned_url = generate_presigned_url(r2_key, expiration=3600)
                if presigned_url:
                    print(f"   ✅ Presigned URL generated successfully")
                    print(f"   URL: {presigned_url[:100]}...")
                else:
                    print(f"   ❌ Failed to generate presigned URL")
            else:
                print(f"   ❌ Document doesn't meet download criteria")

if __name__ == "__main__":
    print("🚀 Testing document download route logic...")
    test_download_logic()
    print("🏁 Testing completed")
