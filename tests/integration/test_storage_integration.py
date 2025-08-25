"""
Storage Integration Tests
Tests for integration between Vercel Blob and Cloudflare R2 storage systems
"""

import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime
from app import app, db, User, RecruitmentDocument, PotentialRecruit
from werkzeug.security import generate_password_hash

class TestStorageSystemIntegration:
    """Test integration between Vercel Blob and Cloudflare R2"""

    def test_full_system_backup_includes_blob_files(self, authenticated_client, test_app, test_db, vercel_blob_mock, cloudflare_r2_mock, storage_test_data):
        """Test that full system backup includes Vercel Blob files"""
        with test_app.app_context():
            # Create test documents in Vercel Blob
            test_content = storage_test_data.create_test_document()

            with vercel_blob_mock.mock_put() as mock_put:
                mock_put.return_value = {
                    'url': 'https://test.vercel-storage.com/test.pdf',
                    'pathname': 'documents/test.pdf',
                    'size': len(test_content)
                }

                # Upload document to Vercel Blob
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    temp_file.write(test_content)
                    temp_file.flush()

                    with open(temp_file.name, 'rb') as f:
                        response = authenticated_client.post('/materials/add-document', data={
                            'title': 'Test Document for Backup',
                            'description': 'Test document for full backup',
                            'file': (f, 'test.pdf')
                        }, content_type='multipart/form-data')

                    os.unlink(temp_file.name)

                    # Verify document was uploaded
                    assert response.status_code in [200, 302], "Document upload failed"

            # Now create full system backup (should include blob files)
            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                with vercel_blob_mock.mock_list() as mock_list:
                    mock_list.return_value = {
                        'blobs': [
                            {
                                'url': 'https://test.vercel-storage.com/test.pdf',
                                'pathname': 'documents/test.pdf',
                                'size': len(test_content)
                            }
                        ]
                    }

                    # Test full backup creation
                    response = authenticated_client.post('/admin/backup', data={
                        'description': 'Full system backup with blob files'
                    })

                    # Verify backup was created
                    assert response.status_code in [200, 302], "Full backup creation failed"

                    # Verify S3 upload was called (for backup)
                    mock_s3.upload_fileobj.assert_called()

    def test_restore_includes_blob_files(self, authenticated_client, test_app, test_db, vercel_blob_mock, cloudflare_r2_mock, storage_test_data):
        """Test that system restore includes blob file restoration"""
        with test_app.app_context():
            # Create test backup data that includes blob file references
            backup_data = {
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

            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                with vercel_blob_mock.mock_put() as mock_put:
                    mock_put.return_value = {
                        'url': 'https://test.vercel-storage.com/test.pdf',
                        'pathname': 'documents/test.pdf',
                        'size': 1024
                    }

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

                        # Verify restoration was successful
                        assert response.status_code in [200, 302], "Backup restoration failed"

                        # Verify blob files were restored
                        mock_put.assert_called()

    def test_storage_system_failover(self, authenticated_client, test_app, test_db, vercel_blob_mock, cloudflare_r2_mock, storage_test_data):
        """Test failover between storage systems"""
        with test_app.app_context():
            test_content = storage_test_data.create_test_document()

            # Test Vercel Blob failover (when blob service is down)
            with patch('vercel_blob.put', side_effect=Exception("Blob service unavailable")):
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    temp_file.write(test_content)
                    temp_file.flush()

                    with open(temp_file.name, 'rb') as f:
                        response = authenticated_client.post('/materials/add-document', data={
                            'title': 'Test Failover Document',
                            'description': 'Test document for failover',
                            'file': (f, 'test.pdf')
                        }, content_type='multipart/form-data')

                    os.unlink(temp_file.name)

                    # Should handle blob service failure gracefully
                    assert response.status_code in [500, 400], "Should handle blob service failure"

            # Test R2 failover (when R2 service is down)
            with patch('boto3.client', side_effect=Exception("R2 service unavailable")):
                response = authenticated_client.post('/admin/backup', data={
                    'description': 'Test R2 failover'
                })

                # Should handle R2 service failure gracefully
                assert response.status_code in [500, 400], "Should handle R2 service failure"

    def test_cross_storage_data_consistency(self, authenticated_client, test_app, test_db, vercel_blob_mock, cloudflare_r2_mock, storage_test_data):
        """Test data consistency between storage systems"""
        with test_app.app_context():
            # Create test document
            test_content = storage_test_data.create_test_document()

            with vercel_blob_mock.mock_put() as mock_put:
                mock_put.return_value = {
                    'url': 'https://test.vercel-storage.com/test.pdf',
                    'pathname': 'documents/test.pdf',
                    'size': len(test_content)
                }

                # Upload document
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    temp_file.write(test_content)
                    temp_file.flush()

                    with open(temp_file.name, 'rb') as f:
                        response = authenticated_client.post('/materials/add-document', data={
                            'title': 'Test Consistency Document',
                            'description': 'Test document for consistency',
                            'file': (f, 'test.pdf')
                        }, content_type='multipart/form-data')

                    os.unlink(temp_file.name)

                    # Verify document was uploaded
                    assert response.status_code in [200, 302], "Document upload failed"

            # Create backup that includes the document
            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                with vercel_blob_mock.mock_list() as mock_list:
                    mock_list.return_value = {
                        'blobs': [
                            {
                                'url': 'https://test.vercel-storage.com/test.pdf',
                                'pathname': 'documents/test.pdf',
                                'size': len(test_content)
                            }
                        ]
                    }

                    # Create backup
                    response = authenticated_client.post('/admin/backup', data={
                        'description': 'Test consistency backup'
                    })

                    # Verify backup was created
                    assert response.status_code in [200, 302], "Backup creation failed"

                    # Verify S3 upload was called
                    mock_s3.upload_fileobj.assert_called()

    def test_storage_system_monitoring(self, authenticated_client, test_app, test_db, vercel_blob_mock, cloudflare_r2_mock):
        """Test monitoring and health checks for both storage systems"""
        with test_app.app_context():
            # Test Vercel Blob health check
            with vercel_blob_mock.mock_list() as mock_list:
                # Test blob listing (health check)
                response = authenticated_client.get('/materials')

                # Verify response
                assert response.status_code == 200, "Blob health check failed"

                # Verify blob list was called
                mock_list.assert_called()

            # Test R2 health check
            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                # Test backup listing (health check)
                response = authenticated_client.get('/admin/database')

                # Verify response
                assert response.status_code == 200, "R2 health check failed"

                # Verify S3 list was called
                mock_s3.list_objects_v2.assert_called()

    def test_storage_system_performance(self, authenticated_client, test_app, test_db, vercel_blob_mock, cloudflare_r2_mock, storage_test_data):
        """Test performance of both storage systems"""
        import time

        with test_app.app_context():
            # Test Vercel Blob upload performance
            test_content = storage_test_data.create_test_document()

            with vercel_blob_mock.mock_put() as mock_put:
                mock_put.return_value = {
                    'url': 'https://test.vercel-storage.com/test.pdf',
                    'pathname': 'documents/test.pdf',
                    'size': len(test_content)
                }

                start_time = time.time()

                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    temp_file.write(test_content)
                    temp_file.flush()

                    with open(temp_file.name, 'rb') as f:
                        response = authenticated_client.post('/materials/add-document', data={
                            'title': 'Test Performance Document',
                            'description': 'Test document for performance',
                            'file': (f, 'test.pdf')
                        }, content_type='multipart/form-data')

                    os.unlink(temp_file.name)

                upload_time = time.time() - start_time

                # Verify upload was successful and within performance limits
                assert response.status_code in [200, 302], "Upload failed"
                assert upload_time < 30.0, f"Upload took too long: {upload_time:.2f} seconds"

            # Test R2 backup performance
            with cloudflare_r2_mock.mock_s3_client() as mock_s3:
                start_time = time.time()

                response = authenticated_client.post('/admin/backup', data={
                    'description': 'Test performance backup'
                })

                backup_time = time.time() - start_time

                # Verify backup was successful and within performance limits
                assert response.status_code in [200, 302], "Backup failed"
                assert backup_time < 60.0, f"Backup took too long: {backup_time:.2f} seconds"
