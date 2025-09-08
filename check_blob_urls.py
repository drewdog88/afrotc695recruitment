from app import app, db, RecruitmentDocument

with app.app_context():
    docs = RecruitmentDocument.query.filter_by(is_active=True).all()
    print('Document blob_url status:')
    for doc in docs:
        print(f'  - {doc.title}')
        print(f'    Filename: {doc.filename}')
        print(f'    Blob URL: {doc.blob_url if doc.blob_url else "NOT SET"}')
        print()
