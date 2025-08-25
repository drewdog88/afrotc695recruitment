"""
Cloudflare R2 Document Storage Utilities

This module provides utilities for uploading, downloading, and managing documents
in Cloudflare R2 storage for the AFROTC 695 recruitment system.
"""

import os
import boto3
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from werkzeug.datastructures import FileStorage

# R2 Configuration
R2_ACCOUNT_ID = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.getenv('CLOUDFLARE_R2_BUCKET_NAME', 'afrotc695recruitment')

def get_r2_client():
    """Create and return R2 client"""
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        raise ValueError("R2 credentials not configured")

    return boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name='auto'
    )

def upload_document_to_r2(file: FileStorage, original_filename: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Upload a document to R2 storage

    Args:
        file: FileStorage object from Flask request
        original_filename: Original filename of the uploaded file

    Returns:
        Tuple of (r2_url, r2_filename, error_message)
    """
    try:
        r2_client = get_r2_client()

        # Generate unique filename for R2
        file_extension = Path(original_filename).suffix
        unique_filename = f"documents/{uuid.uuid4().hex}_{original_filename}"

        # Determine content type based on file extension
        content_type = get_content_type(file_extension)

        # Upload to R2
        r2_client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=unique_filename,
            Body=file.read(),
            ContentType=content_type
        )

        # Generate public URL
        r2_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{R2_BUCKET_NAME}/{unique_filename}"

        return r2_url, unique_filename, None

    except Exception as e:
        return None, None, str(e)

def delete_document_from_r2(r2_filename: str) -> bool:
    """
    Delete a document from R2 storage

    Args:
        r2_filename: The R2 filename/key to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        r2_client = get_r2_client()
        r2_client.delete_object(Bucket=R2_BUCKET_NAME, Key=r2_filename)
        return True
    except Exception as e:
        print(f"Error deleting document from R2: {e}")
        return False

def get_document_url(r2_filename: str) -> Optional[str]:
    """
    Get the public URL for a document in R2

    Args:
        r2_filename: The R2 filename/key

    Returns:
        Public URL for the document
    """
    if not r2_filename:
        return None

    # Check if custom domain is configured
    custom_domain = os.getenv('CLOUDFLARE_R2_CUSTOM_DOMAIN')
    if custom_domain:
        return f"https://{custom_domain}/{r2_filename}"
    else:
        # Use direct R2 endpoint (may require authentication)
        return f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{R2_BUCKET_NAME}/{r2_filename}"

def generate_presigned_url(r2_filename: str, expiration: int = 3600) -> Optional[str]:
    """
    Generate a presigned URL for secure document download

    Args:
        r2_filename: The R2 filename/key
        expiration: URL expiration time in seconds (default: 1 hour)

    Returns:
        Presigned URL for the document
    """
    if not r2_filename:
        return None

    try:
        r2_client = get_r2_client()
        presigned_url = r2_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': R2_BUCKET_NAME,
                'Key': r2_filename
            },
            ExpiresIn=expiration
        )
        return presigned_url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

def get_content_type(file_extension: str) -> str:
    """
    Get the appropriate content type for a file extension

    Args:
        file_extension: File extension (e.g., '.pdf', '.docx')

    Returns:
        Content type string
    """
    content_types = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.txt': 'text/plain',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif'
    }

    return content_types.get(file_extension.lower(), 'application/octet-stream')

def validate_file_type(filename: str) -> bool:
    """
    Validate if the file type is allowed

    Args:
        filename: Name of the file to validate

    Returns:
        True if file type is allowed, False otherwise
    """
    allowed_extensions = {'.pdf', '.ppt', '.pptx', '.doc', '.docx', '.xls', '.xlsx', '.txt'}
    file_extension = Path(filename).suffix.lower()
    return file_extension in allowed_extensions

def get_file_size_mb(file: FileStorage) -> float:
    """
    Get file size in megabytes

    Args:
        file: FileStorage object

    Returns:
        File size in MB
    """
    # Reset file pointer to beginning
    file.seek(0, 2)  # Seek to end
    size_bytes = file.tell()
    file.seek(0)  # Reset to beginning
    return size_bytes / (1024 * 1024)

def validate_file_size(file: FileStorage, max_size_mb: float = 10.0) -> bool:
    """
    Validate if file size is within limits

    Args:
        file: FileStorage object
        max_size_mb: Maximum file size in MB

    Returns:
        True if file size is acceptable, False otherwise
    """
    file_size_mb = get_file_size_mb(file)
    return file_size_mb <= max_size_mb

def is_r2_configured() -> bool:
    """
    Check if R2 is properly configured

    Returns:
        True if R2 is configured, False otherwise
    """
    return all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY])

def get_r2_config_status() -> Dict[str, Any]:
    """
    Get R2 configuration status

    Returns:
        Dictionary with configuration status
    """
    return {
        'account_id_configured': bool(R2_ACCOUNT_ID),
        'access_key_configured': bool(R2_ACCESS_KEY_ID),
        'secret_key_configured': bool(R2_SECRET_ACCESS_KEY),
        'bucket_configured': bool(R2_BUCKET_NAME),
        'fully_configured': is_r2_configured()
    }
