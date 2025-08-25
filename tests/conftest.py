"""
Pytest configuration for AFROTC 695 Recruitment Management System
Includes storage-specific test fixtures for Vercel Blob and Cloudflare R2
"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from app import app, db
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

@pytest.fixture(scope='session')
def test_app():
    """Create test app with proper storage configuration"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    # Test database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_DATABASE_URL', 'postgresql://test:test@localhost/test_db')

    # Storage configuration for testing
    app.config['VERCEL_BLOB_ENABLED'] = True
    app.config['CLOUDFLARE_R2_ENABLED'] = True

    return app

@pytest.fixture
def test_client(test_app):
    """Create test client"""
    return test_app.test_client()

@pytest.fixture
def test_db(test_app):
    """Create test database with cleanup"""
    with test_app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def authenticated_client(test_client, test_app, test_db):
    """Create an authenticated test client with a test user"""
    from app import User
    from werkzeug.security import generate_password_hash

    with test_app.app_context():
        # Create test user with shorter password hash for testing
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash='pbkdf2:sha256:600000$test$hash$for$testing',  # Use shorter hash for testing
            first_name='Test',
            last_name='User',
            role='admin',
            secret_question='What is your favorite color?',
            secret_answer_hash='pbkdf2:sha256:600000$test$answer$hash'  # Use shorter hash for testing
        )
        test_db.session.add(test_user)
        test_db.session.commit()

        # Login the user
        test_client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)

        return test_client

@pytest.fixture
def storage_test_data():
    """Provide test data for storage operations"""
    class StorageTestData:
        @staticmethod
        def create_test_document():
            """Create a simple test PDF document"""
            return b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test Document) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF\n'

        @staticmethod
        def create_test_backup():
            """Create test backup data"""
            return {
                'database': 'test_db',
                'timestamp': '2024-01-01T00:00:00Z',
                'tables': ['users', 'recruits', 'cadets', 'recruitment_document'],
                'data': 'test backup content',
                'vercel_blob_files': [
                    {
                        'url': 'https://test.vercel-storage.com/test.pdf',
                        'pathname': 'documents/test.pdf',
                        'size': 1024
                    }
                ]
            }

        @staticmethod
        def create_temp_file(content, extension='.txt'):
            """Create a temporary file for testing"""
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
            temp_file.write(content)
            temp_file.close()
            return temp_file.name

    return StorageTestData()

@pytest.fixture
def vercel_blob_mock():
    """Mock Vercel Blob operations"""
    class VercelBlobMock:
        @staticmethod
        def mock_put():
            return patch('vercel_blob.put')

        @staticmethod
        def mock_list():
            return patch('vercel_blob.list')

        @staticmethod
        def mock_delete():
            return patch('vercel_blob.del_')

        @staticmethod
        def mock_head():
            return patch('vercel_blob.head')

    return VercelBlobMock()

@pytest.fixture
def cloudflare_r2_mock():
    """Mock Cloudflare R2 operations"""
    class CloudflareR2Mock:
        @staticmethod
        def mock_s3_client():
            mock_client = MagicMock()
            mock_client.upload_fileobj.return_value = None
            mock_client.download_fileobj.return_value = None
            mock_client.delete_object.return_value = None
            mock_client.list_objects_v2.return_value = {
                'Contents': [
                    {
                        'Key': 'test_backup.json',
                        'Size': 1024,
                        'LastModified': '2024-01-01T00:00:00Z'
                    }
                ]
            }
            return patch('boto3.client', return_value=mock_client)

    return CloudflareR2Mock()

@pytest.fixture
def storage_environment_check():
    """Check storage environment configuration"""
    def check_environment():
        # Check Vercel Blob environment
        blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
        vercel_blob_configured = blob_token is not None and len(blob_token) > 0

        # Check Cloudflare R2 environment
        r2_access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
        r2_secret_key = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
        r2_account_id = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
        r2_bucket = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')

        r2_configured = all([
            r2_access_key is not None and len(r2_access_key) > 0,
            r2_secret_key is not None and len(r2_secret_key) > 0,
            r2_account_id is not None and len(r2_account_id) > 0,
            r2_bucket is not None and len(r2_bucket) > 0
        ])

        return {
            'vercel_blob_configured': vercel_blob_configured,
            'cloudflare_r2_configured': r2_configured,
            'blob_token_set': vercel_blob_configured,
            'r2_credentials_set': r2_configured
        }

    return check_environment
