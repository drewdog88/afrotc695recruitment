#!/usr/bin/env python3
"""
Comprehensive tests for AFROTC 695 Backup Functionality
Tests blob list handling, file downloading, and ZIP creation
"""

import os
import unittest
import tempfile
import zipfile
import json
import io
from datetime import datetime
from unittest.mock import patch, MagicMock
import requests

# Add the project directory to the Python path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neon_backup_scheduler import (
    create_full_backup_zip,
    download_backup_file_by_url,
    backup_database_neon,
    list_backup_files
)

class TestBackupFunctionality(unittest.TestCase):
    """Test suite for backup functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_files = {
            'test_document.pdf': b'PDF content for testing',
            'images/logo.png': b'PNG image data for testing',
            'data/config.json': b'{"key": "value", "test": true}',
            'backups/test_backup.json': b'{"backup": "data", "timestamp": "2024-01-01"}',
            'documents/afrotc_handbook.pdf': b'AFROTC handbook content'
        }

        # Mock blob list response structure
        self.mock_blob_list_response = {
            'blobs': [
                {
                    'pathname': 'test_document.pdf',
                    'url': 'https://blob.vercel-storage.com/test_document.pdf',
                    'size': 25
                },
                {
                    'pathname': 'images/logo.png',
                    'url': 'https://blob.vercel-storage.com/images/logo.png',
                    'size': 24
                },
                {
                    'pathname': 'data/config.json',
                    'url': 'https://blob.vercel-storage.com/data/config.json',
                    'size': 30
                },
                {
                    'pathname': 'backups/test_backup.json',
                    'url': 'https://blob.vercel-storage.com/backups/test_backup.json',
                    'size': 45
                },
                {
                    'pathname': 'documents/afrotc_handbook.pdf',
                    'url': 'https://blob.vercel-storage.com/documents/afrotc_handbook.pdf',
                    'size': 28
                }
            ]
        }

    def test_blob_list_structure(self):
        """Test that blob_list() returns expected structure"""
        # This test verifies our understanding of the blob_list() response format
        expected_keys = ['blobs']

        # Mock the blob_list function
        with patch('neon_backup_scheduler.blob_list') as mock_blob_list:
            mock_blob_list.return_value = self.mock_blob_list_response

            # Test the structure
            response = mock_blob_list()

            self.assertIsInstance(response, dict)
            self.assertIn('blobs', response)
            self.assertIsInstance(response['blobs'], list)

            # Test individual blob structure
            for blob in response['blobs']:
                self.assertIn('pathname', blob)
                self.assertIn('url', blob)
                self.assertIn('size', blob)

    def test_download_backup_file_by_url_success(self):
        """Test successful file download from URL"""
        test_url = 'https://blob.vercel-storage.com/test_file.txt'
        test_content = b'Test file content'

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = test_content
            mock_get.return_value = mock_response

            result = download_backup_file_by_url(test_url)

            self.assertEqual(result, test_content)
            mock_get.assert_called_once_with(test_url)

    def test_download_backup_file_by_url_failure(self):
        """Test file download failure handling"""
        test_url = 'https://blob.vercel-storage.com/nonexistent.txt'

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = download_backup_file_by_url(test_url)

            self.assertIsNone(result)

    def test_download_backup_file_by_url_network_error(self):
        """Test network error handling"""
        test_url = 'https://blob.vercel-storage.com/test_file.txt'

        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")

            result = download_backup_file_by_url(test_url)

            self.assertIsNone(result)

    @patch('neon_backup_scheduler.blob_list')
    @patch('neon_backup_scheduler.backup_database_neon')
    @patch('neon_backup_scheduler.put')
    @patch('requests.get')
    def test_create_full_backup_zip_structure(self, mock_requests_get, mock_put, mock_backup_db, mock_blob_list):
        """Test that full backup ZIP contains expected files"""
        # Mock database backup
        mock_backup_db.return_value = ('backups/full/test_db.json', 'https://blob.vercel-storage.com/test_db.json')

        # Mock blob list response
        mock_blob_list.return_value = self.mock_blob_list_response

        # Mock file downloads
        def mock_get(url):
            mock_response = MagicMock()
            mock_response.status_code = 200
            # Return different content based on URL
            if 'test_document.pdf' in url:
                mock_response.content = self.test_files['test_document.pdf']
            elif 'logo.png' in url:
                mock_response.content = self.test_files['images/logo.png']
            elif 'config.json' in url:
                mock_response.content = self.test_files['data/config.json']
            elif 'test_backup.json' in url:
                mock_response.content = self.test_files['backups/test_backup.json']
            elif 'afrotc_handbook.pdf' in url:
                mock_response.content = self.test_files['documents/afrotc_handbook.pdf']
            else:
                mock_response.content = b'unknown file'
            return mock_response

        mock_requests_get.side_effect = mock_get

        # Mock blob upload
        mock_put.return_value = {'url': 'https://blob.vercel-storage.com/backup.zip'}

        # Create backup
        result = create_full_backup_zip("Test backup")

        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

        # Verify the ZIP was uploaded
        mock_put.assert_called_once()
        zip_content = mock_put.call_args[0][1]  # Second argument is the ZIP content

        # Verify ZIP structure
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            file_list = zip_file.namelist()

            # Should contain database backup
            self.assertIn('database_backup.json', file_list)

            # Should contain all blob files
            self.assertIn('blob_contents/test_document.pdf', file_list)
            self.assertIn('blob_contents/images/logo.png', file_list)
            self.assertIn('blob_contents/data/config.json', file_list)
            self.assertIn('blob_contents/backups/test_backup.json', file_list)
            self.assertIn('blob_contents/documents/afrotc_handbook.pdf', file_list)

            # Should contain metadata
            self.assertIn('backup_metadata.json', file_list)

            # Verify file contents
            with zip_file.open('blob_contents/test_document.pdf') as f:
                self.assertEqual(f.read(), self.test_files['test_document.pdf'])

            with zip_file.open('blob_contents/data/config.json') as f:
                self.assertEqual(f.read(), self.test_files['data/config.json'])

    @patch('neon_backup_scheduler.blob_list')
    @patch('neon_backup_scheduler.backup_database_neon')
    @patch('neon_backup_scheduler.put')
    @patch('requests.get')
    def test_backup_excludes_self(self, mock_requests_get, mock_put, mock_backup_db, mock_blob_list):
        """Test that backup doesn't include itself"""
        # Mock database backup
        mock_backup_db.return_value = ('backups/full/test_db.json', 'https://blob.vercel-storage.com/test_db.json')

        # Mock blob list response including the backup we're creating
        blob_response = {
            'blobs': [
                {
                    'pathname': 'backups/full/afrotc695_full_backup_20241201_120000.zip',
                    'url': 'https://blob.vercel-storage.com/backup.zip',
                    'size': 1000
                },
                {
                    'pathname': 'test_document.pdf',
                    'url': 'https://blob.vercel-storage.com/test_document.pdf',
                    'size': 25
                }
            ]
        }
        mock_blob_list.return_value = blob_response

        # Mock file downloads
        def mock_get(url):
            mock_response = MagicMock()
            mock_response.status_code = 200
            if 'test_document.pdf' in url:
                mock_response.content = self.test_files['test_document.pdf']
            else:
                mock_response.content = b'unknown file'
            return mock_response

        mock_requests_get.side_effect = mock_get

        # Mock blob upload
        mock_put.return_value = {'url': 'https://blob.vercel-storage.com/backup.zip'}

        # Create backup
        result = create_full_backup_zip("Test backup")

        # Verify the ZIP was uploaded
        mock_put.assert_called_once()
        zip_content = mock_put.call_args[0][1]

        # Verify ZIP structure - should NOT contain the backup file itself
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            file_list = zip_file.namelist()

            # Should NOT contain the backup file itself
            self.assertNotIn('blob_contents/backups/full/afrotc695_full_backup_20241201_120000.zip', file_list)

            # Should contain other files
            self.assertIn('blob_contents/test_document.pdf', file_list)

    @patch('neon_backup_scheduler.blob_list')
    @patch('neon_backup_scheduler.backup_database_neon')
    @patch('neon_backup_scheduler.put')
    def test_backup_metadata_accuracy(self, mock_put, mock_backup_db, mock_blob_list):
        """Test that backup metadata reflects actual contents"""
        # Mock database backup
        mock_backup_db.return_value = ('backups/full/test_db.json', 'https://blob.vercel-storage.com/test_db.json')

        # Mock blob list response
        mock_blob_list.return_value = self.mock_blob_list_response

        # Mock blob upload
        mock_put.return_value = {'url': 'https://blob.vercel-storage.com/backup.zip'}

        # Create backup
        result = create_full_backup_zip("Test backup")

        # Verify the ZIP was uploaded
        mock_put.assert_called_once()
        zip_content = mock_put.call_args[0][1]

        # Verify metadata
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            with zip_file.open('backup_metadata.json') as f:
                metadata = json.loads(f.read().decode('utf-8'))

                # Check metadata structure
                self.assertIn('timestamp', metadata)
                self.assertIn('description', metadata)
                self.assertIn('backup_type', metadata)
                self.assertIn('created_at', metadata)
                self.assertIn('contents', metadata)

                # Check contents
                contents = metadata['contents']
                self.assertIn('database_backup', contents)
                self.assertIn('blob_files_count', contents)
                self.assertIn('total_size', contents)

                # Verify blob files count matches expected
                self.assertEqual(contents['blob_files_count'], 5)  # 5 test files
                self.assertEqual(metadata['description'], 'Test backup')
                self.assertEqual(metadata['backup_type'], 'full')

    @patch('neon_backup_scheduler.blob_list')
    @patch('neon_backup_scheduler.backup_database_neon')
    @patch('neon_backup_scheduler.put')
    @patch('requests.get')
    def test_empty_blob_store_backup(self, mock_requests_get, mock_put, mock_backup_db, mock_blob_list):
        """Test backup creation with empty blob store"""
        # Mock database backup
        mock_backup_db.return_value = ('backups/full/test_db.json', 'https://blob.vercel-storage.com/test_db.json')

        # Mock database backup download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"database": "backup content"}'
        mock_requests_get.return_value = mock_response

        # Mock empty blob list
        mock_blob_list.return_value = {'blobs': []}

        # Mock blob upload
        mock_put.return_value = {'url': 'https://blob.vercel-storage.com/backup.zip'}

        # Create backup
        result = create_full_backup_zip("Empty store backup")

        # Verify the ZIP was uploaded
        mock_put.assert_called_once()
        zip_content = mock_put.call_args[0][1]

        # Verify ZIP structure - should only contain database and metadata
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            file_list = zip_file.namelist()

            # Should contain database backup
            self.assertIn('database_backup.json', file_list)

            # Should contain metadata
            self.assertIn('backup_metadata.json', file_list)

            # Should NOT contain blob_contents folder
            blob_files = [f for f in file_list if f.startswith('blob_contents/')]
            self.assertEqual(len(blob_files), 0)

    @patch('neon_backup_scheduler.blob_list')
    @patch('neon_backup_scheduler.backup_database_neon')
    @patch('neon_backup_scheduler.put')
    def test_backup_with_download_failures(self, mock_put, mock_backup_db, mock_blob_list):
        """Test backup creation when some files fail to download"""
        # Mock database backup
        mock_backup_db.return_value = ('backups/full/test_db.json', 'https://blob.vercel-storage.com/test_db.json')

        # Mock blob list response
        mock_blob_list.return_value = self.mock_blob_list_response

        # Mock blob upload
        mock_put.return_value = {'url': 'https://blob.vercel-storage.com/backup.zip'}

        # Mock file downloads with some failures
        def mock_get(url):
            mock_response = MagicMock()
            if 'logo.png' in url:
                # Simulate download failure for logo.png
                mock_response.status_code = 404
            else:
                mock_response.status_code = 200
                if 'test_document.pdf' in url:
                    mock_response.content = self.test_files['test_document.pdf']
                elif 'config.json' in url:
                    mock_response.content = self.test_files['data/config.json']
                elif 'test_backup.json' in url:
                    mock_response.content = self.test_files['backups/test_backup.json']
                elif 'afrotc_handbook.pdf' in url:
                    mock_response.content = self.test_files['documents/afrotc_handbook.pdf']
                else:
                    mock_response.content = b'unknown file'
            return mock_response

        with patch('requests.get', side_effect=mock_get):
            # Create backup
            result = create_full_backup_zip("Test backup with failures")

            # Verify the ZIP was uploaded
            mock_put.assert_called_once()
            zip_content = mock_put.call_args[0][1]

            # Verify ZIP structure - should contain successful downloads
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
                file_list = zip_file.namelist()

                # Should contain successful downloads
                self.assertIn('blob_contents/test_document.pdf', file_list)
                self.assertIn('blob_contents/data/config.json', file_list)
                self.assertIn('blob_contents/backups/test_backup.json', file_list)
                self.assertIn('blob_contents/documents/afrotc_handbook.pdf', file_list)

                # Should NOT contain failed download
                self.assertNotIn('blob_contents/images/logo.png', file_list)

    def test_list_backup_files_structure(self):
        """Test list_backup_files function structure"""
        with patch('neon_backup_scheduler.blob_list') as mock_blob_list:
            # Mock response with backup files
            mock_response = {
                'blobs': [
                    {
                        'pathname': 'backups/afrotc695_backup_20241201_120000.json',
                        'url': 'https://blob.vercel-storage.com/backup1.json',
                        'size': 1000
                    },
                    {
                        'pathname': 'backups/full/afrotc695_full_backup_20241201_130000.zip',
                        'url': 'https://blob.vercel-storage.com/backup2.zip',
                        'size': 5000
                    }
                ]
            }
            mock_blob_list.return_value = mock_response

            # Mock head function for file info
            with patch('neon_backup_scheduler.head') as mock_head:
                mock_head.return_value = {'size': 1000}

                # Test list_backup_files
                backup_files = list_backup_files()

                # Verify structure
                self.assertIsInstance(backup_files, list)
                self.assertEqual(len(backup_files), 2)

                for backup_file in backup_files:
                    self.assertIn('filename', backup_file)
                    self.assertIn('backup_type', backup_file)
                    self.assertIn('created', backup_file)
                    self.assertIn('size', backup_file)
                    self.assertIn('description', backup_file)
                    self.assertIn('user', backup_file)

if __name__ == '__main__':
    unittest.main()
