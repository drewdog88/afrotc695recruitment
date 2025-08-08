from api.app import app, db, ExternalLink, RecruitmentDocument
from datetime import datetime

def restore_materials():
    """Restore missing external links and documents from the backup"""
    
    with app.app_context():
        print("=== RESTORING EXTERNAL LINKS ===")
        
        # External links from the backup
        links_data = [
            {
                'title': 'AFROTC Official Website',
                'url': 'https://www.afrotc.com/',
                'description': 'Official Air Force ROTC website with information about the program, scholarships, and careers.',
                'category': 'official',
                'is_active': True,
                'sort_order': 1
            },
            {
                'title': 'University of Portland AFROTC',
                'url': 'https://www.up.edu/afrotc/',
                'description': 'AFROTC Detachment 695 at University of Portland - local program information and contact details.',
                'category': 'official',
                'is_active': True,
                'sort_order': 2
            },
            {
                'title': 'U.S. Air Force',
                'url': 'https://www.af.mil/',
                'description': 'Official U.S. Air Force website with information about careers, missions, and news.',
                'category': 'official',
                'is_active': True,
                'sort_order': 3
            },
            {
                'title': 'U.S. Space Force',
                'url': 'https://www.spaceforce.mil/',
                'description': 'Official U.S. Space Force website with information about space operations and careers.',
                'category': 'official',
                'is_active': True,
                'sort_order': 4
            },
            {
                'title': 'The Holm Center',
                'url': 'https://www.airuniversity.af.edu/Holm-Center/',
                'description': 'Air University Holm Center for Officer Accessions and Citizen Development.',
                'category': 'official',
                'is_active': True,
                'sort_order': 5
            }
        ]
        
        # Add external links
        for link_data in links_data:
            # Check if link already exists
            existing = ExternalLink.query.filter_by(url=link_data['url']).first()
            if not existing:
                link = ExternalLink(**link_data)
                db.session.add(link)
                print(f"Added: {link_data['title']}")
            else:
                print(f"Already exists: {link_data['title']}")
        
        print("\n=== RESTORING DOCUMENT ===")
        
        # Document from the backup (already in blob storage)
        doc_data = {
            'title': 'Scholarship Application for AFROTC',
            'description': 'AFROTC High School Scholarship Program (HSSP) Application Guide for Academic Year 2026-27',
            'filename': '35dab357e1534d27b5fac0c7ad50d71b_d0e97453f5db476b92807b2345d3ec44_1.-AY26-27_HSSP_Applicant_Guide-Signed.pdf',
            'original_filename': '1.-AY26-27_HSSP_Applicant_Guide-Signed.pdf',
            'file_size': 606987,
            'file_type': 'pdf',
            'category': 'forms',
            'is_active': True,
            'sort_order': 0
        }
        
        # Check if document already exists
        existing_doc = RecruitmentDocument.query.filter_by(filename=doc_data['filename']).first()
        if not existing_doc:
            doc = RecruitmentDocument(**doc_data)
            db.session.add(doc)
            print(f"Added: {doc_data['title']}")
        else:
            print(f"Already exists: {doc_data['title']}")
        
        # Commit changes
        db.session.commit()
        print("\n=== RESTORATION COMPLETE ===")
        
        # Verify
        print(f"\nExternal Links: {ExternalLink.query.count()}")
        print(f"Documents: {RecruitmentDocument.query.count()}")

if __name__ == '__main__':
    restore_materials()
