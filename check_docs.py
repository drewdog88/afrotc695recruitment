from app import app, db, RecruitmentDocument

with app.app_context():
    docs = RecruitmentDocument.query.filter_by(is_active=True).all()
    print('Document details:')
    for doc in docs:
        print(f'  - {doc.title}')
        print(f'    Filename: {doc.filename}')
        print(f'    Has blob_url attr: {hasattr(doc, "blob_url")}')
        if hasattr(doc, 'blob_url'):
            print(f'    Blob URL: {doc.blob_url}')
        print()
