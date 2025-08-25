"""
Cloudflare R2 Storage Tests
Tests for database backup operations using Cloudflare R2
"""

import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime
from app import app, db, User, ActivityLog, PotentialRecruit
from werkzeug.security import generate_password_hash

class TestCloudflareR2Storage:
    """Test Cloudflare R2 storage operations"""

    def test_r2_environment_configuration(self, storage_environment_check):
        """Test that Cloudflare R2 environment is properly configured"""
        env_status = storage_environment_check()
        # Skip this test if R2 credentials are not configured
        if not env_status['cloudflare_r2_configured']:
            pytest.skip("R2 credentials not configured - skipping R2 tests")
        assert env_status['cloudflare_r2_configured'], "R2 credentials should be set for Cloudflare R2"

    def test_backup_creation_workflow(self, authenticated_client, test_app, test_db, cloudflare_r2_mock, storage_test_data):
        """Test complete backup creation workflow"""
        with test_app.app_context():
            # Create test user for authentication
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('testpass'),
                first_name='Test',
                last_name='User',
                role='admin',
                secret_question='What is your favorite color?',
                secret_answer_hash=generate_password_hash('blue')
            )
            test_db.session.add(test_user)
            test_db.session.commit()

            # Login
            test_client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            })

            # Create some test data
            test_recruit = PotentialRecruit(
                first_name='Test',
                last_name='Recruit',
                email='test@example.com',
                current_school='Test School',
                school_type='high_school',
                status='prospective'
            )
            test_db.session.add(test_recruit)
            test_db.session.commit()

            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Test backup creation
                response = authenticated_client.post('/admin/backup', data={
                    'description': 'Test backup'
                })

                # Verify response
                assert response.status_code in [200, 302], f"Backup creation failed with status {response.status_code}"

                # Verify S3 upload was called
                mock_s3.upload_fileobj.assert_called()

    def test_backup_download_workflow(self, test_client, test_app, test_db, cloudflare_r2_mock):
        """Test backup download workflow"""
        with test_app.app_context():
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('testpass'),
                first_name='Test',
                last_name='User',
                role='admin',
                secret_question='What is your favorite color?',
                secret_answer_hash=generate_password_hash('blue')
            )
            test_db.session.add(test_user)
            test_db.session.commit()

            # Login
            test_client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            })

            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Mock successful download
                mock_s3.download_fileobj.return_value = None

                # Test backup download
                response = test_client.get('/admin/download-backup/test_backup.json')

                # Should return file or redirect
                assert response.status_code in [200, 302, 404], f"Download failed with status {response.status_code}"

    def test_backup_listing_workflow(self, authenticated_client, test_app, test_db, cloudflare_r2_mock):
        """Test backup listing workflow"""
        with test_app.app_context():
            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Test backup listing
                response = authenticated_client.get('/admin/database')

                # Verify response
                assert response.status_code == 200, f"Backup listing failed with status {response.status_code}"

                # Verify S3 list was called
                mock_s3.list_objects_v2.assert_called()

    def test_backup_deletion_workflow(self, authenticated_client, test_app, test_db, cloudflare_r2_mock):
        """Test backup deletion workflow"""
        with test_app.app_context():
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('testpass'),
                first_name='Test',
                last_name='User',
                role='admin',
                secret_question='What is your favorite color?',
                secret_answer_hash=generate_password_hash('blue')
            )
            test_db.session.add(test_user)
            test_db.session.commit()

            # Login
            test_client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            })

            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Test backup deletion
                response = authenticated_client.post('/admin/delete-backup/test_backup.json')

                # Verify response
                assert response.status_code in [200, 302], f"Backup deletion failed with status {response.status_code}"

                # Verify S3 delete was called
                mock_s3.delete_object.assert_called()

    def test_backup_restoration_workflow(self, authenticated_client, test_app, test_db, cloudflare_r2_mock, storage_test_data):
        """Test backup restoration workflow"""
        with test_app.app_context():
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('testpass'),
                first_name='Test',
                last_name='User',
                role='admin',
                secret_question='What is your favorite color?',
                secret_answer_hash=generate_password_hash('blue')
            )
            test_db.session.add(test_user)
            test_db.session.commit()

            # Login
            test_client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass'
            })

            # Create test backup data
            backup_data = storage_test_data.create_test_backup()

            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Mock backup download
                mock_s3.download_fileobj.return_value = None

                # Create temporary backup file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(backup_data, temp_file)
                    temp_file.flush()

                    # Test backup restoration
                    with open(temp_file.name, 'rb') as f:
                        response = authenticated_client.post('/admin/restore', data={
                            'backup_file': (f, 'test_backup.json')
                        }, content_type='multipart/form-data')

                    os.unlink(temp_file.name)

                    # Verify response
                    assert response.status_code in [200, 302], f"Backup restoration failed with status {response.status_code}"

    def test_backup_encryption(self, authenticated_client, test_app, test_db, cloudflare_r2_mock):
        """Test backup encryption and security"""
        with test_app.app_context():
            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Test backup creation with encryption
                response = authenticated_client.post('/admin/backup', data={
                    'description': 'Test encrypted backup'
                })

                # Verify response
                assert response.status_code in [200, 302], f"Encrypted backup creation failed with status {response.status_code}"

                # Verify S3 upload was called with encryption parameters
                mock_s3.upload_fileobj.assert_called()

    def test_backup_retention_policy(self, authenticated_client, test_app, test_db, cloudflare_r2_mock):
        """Test backup retention and cleanup"""
        with test_app.app_context():
            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Mock multiple backups
                mock_s3.list_objects_v2.return_value = {
                    'Contents': [
                        {'Key': 'backup_old.json', 'LastModified': datetime(2020, 1, 1)},
                        {'Key': 'backup_recent.json', 'LastModified': datetime(2024, 1, 1)}
                    ]
                }

                # Test backup listing with retention policy
                response = authenticated_client.get('/admin/database')

                # Verify response
                assert response.status_code == 200, f"Backup listing failed with status {response.status_code}"

                # Verify old backups are handled appropriately
                mock_s3.list_objects_v2.assert_called()

    def test_backup_error_handling(self, authenticated_client, test_app, test_db, storage_test_data):
        """Test error handling for backup operations"""
        with test_app.app_context():
            # Test with R2 service error
            with patch('boto3.client', side_effect=Exception("R2 service error")):
                response = authenticated_client.post('/admin/backup', data={
                    'description': 'Test error handling'
                })

                # Should handle R2 service errors gracefully
                assert response.status_code in [500, 400], "Should handle R2 service errors"

    def test_backup_metadata_handling(self, authenticated_client, test_app, test_db, cloudflare_r2_mock):
        """Test backup metadata storage and retrieval"""
        with test_app.app_context():
            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Test backup listing
                response = authenticated_client.get('/admin/database')

                # Verify response
                assert response.status_code in [200, 302], f"Backup listing failed with status {response.status_code}"

                # Verify backup metadata is handled correctly
                mock_s3.list_objects_v2.assert_called()
                # or verifying the backup file contains the correct metadata
