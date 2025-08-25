#!/usr/bin/env python3
"""
R2 Coverage Report Utilities

This module provides utility functions for managing code coverage reports
in Cloudflare R2 storage, replacing the previous Vercel Blob implementation.
"""

import os
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

# R2 Configuration
R2_ACCOUNT_ID = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.getenv('CLOUDFLARE_R2_BUCKET_NAME', 'afrotc695recruitment')
R2_CUSTOM_DOMAIN = os.getenv('CLOUDFLARE_R2_CUSTOM_DOMAIN')

def get_r2_client():
    """Get R2 client for coverage report operations"""
    try:
        if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME]):
            print("Warning: R2 credentials not fully configured")
            return None

        r2_client = boto3.client(
            's3',
            endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            region_name='auto'
        )
        return r2_client
    except Exception as e:
        print(f"Error creating R2 client: {e}")
        return None

def upload_coverage_report(coverage_data, filename=None):
    """
    Upload coverage report to R2 storage

    Args:
        coverage_data (dict): Coverage report data
        filename (str, optional): Custom filename. If None, generates timestamped filename

    Returns:
        dict: Upload result with success status and file info
    """
    try:
        r2_client = get_r2_client()
        if not r2_client:
            return {'success': False, 'error': 'R2 client not available'}

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/coverage-summary_{timestamp}.json"

        # Ensure reports prefix
        if not filename.startswith('reports/'):
            filename = f"reports/{filename}"

        # Convert coverage data to JSON
        coverage_json = json.dumps(coverage_data, indent=2)

        # Upload to R2
        response = r2_client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=filename,
            Body=coverage_json.encode('utf-8'),
            ContentType='application/json',
            Metadata={
                'uploaded_at': datetime.now().isoformat(),
                'report_type': 'coverage',
                'version': '1.0'
            }
        )

        # Generate URL
        if R2_CUSTOM_DOMAIN:
            file_url = f"https://{R2_CUSTOM_DOMAIN}/{filename}"
        else:
            file_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{R2_BUCKET_NAME}/{filename}"

        return {
            'success': True,
            'filename': filename,
            'url': file_url,
            'size': len(coverage_json),
            'etag': response.get('ETag', '').strip('"'),
            'uploaded_at': datetime.now().isoformat()
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}

def list_coverage_reports(limit=10):
    """
    List coverage reports in R2 storage

    Args:
        limit (int): Maximum number of reports to return

    Returns:
        list: List of coverage report metadata
    """
    try:
        r2_client = get_r2_client()
        if not r2_client:
            return []

        response = r2_client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            Prefix='reports/coverage-summary_',
            MaxKeys=limit
        )

        reports = []
        if 'Contents' in response:
            for obj in response['Contents']:
                reports.append({
                    'filename': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'].strip('"')
                })

        # Sort by last modified (newest first)
        reports.sort(key=lambda x: x['last_modified'], reverse=True)
        return reports

    except Exception as e:
        print(f"Error listing coverage reports: {e}")
        return []

def get_latest_coverage_report():
    """
    Get the most recent coverage report from R2

    Returns:
        dict: Coverage report data or None if not found
    """
    try:
        reports = list_coverage_reports(limit=1)
        if not reports:
            return None

        latest_report = reports[0]
        return download_coverage_report(latest_report['filename'])

    except Exception as e:
        print(f"Error getting latest coverage report: {e}")
        return None

def download_coverage_report(filename):
    """
    Download coverage report from R2

    Args:
        filename (str): Name of the coverage report file

    Returns:
        dict: Coverage report data or None if not found
    """
    try:
        r2_client = get_r2_client()
        if not r2_client:
            return None

        # Ensure reports prefix
        if not filename.startswith('reports/'):
            filename = f"reports/{filename}"

        response = r2_client.get_object(
            Bucket=R2_BUCKET_NAME,
            Key=filename
        )

        content = response['Body'].read().decode('utf-8')
        return json.loads(content)

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"Coverage report not found: {filename}")
        else:
            print(f"Error downloading coverage report: {e}")
        return None
    except Exception as e:
        print(f"Error downloading coverage report: {e}")
        return None

def delete_coverage_report(filename):
    """
    Delete coverage report from R2

    Args:
        filename (str): Name of the coverage report file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        r2_client = get_r2_client()
        if not r2_client:
            return False

        # Ensure reports prefix
        if not filename.startswith('reports/'):
            filename = f"reports/{filename}"

        r2_client.delete_object(
            Bucket=R2_BUCKET_NAME,
            Key=filename
        )

        return True

    except Exception as e:
        print(f"Error deleting coverage report: {e}")
        return False

def generate_presigned_url(filename, expiration=3600):
    """
    Generate presigned URL for coverage report download

    Args:
        filename (str): Name of the coverage report file
        expiration (int): URL expiration time in seconds (default: 1 hour)

    Returns:
        str: Presigned URL or None if error
    """
    try:
        r2_client = get_r2_client()
        if not r2_client:
            return None

        # Ensure reports prefix
        if not filename.startswith('reports/'):
            filename = f"reports/{filename}"

        url = r2_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': R2_BUCKET_NAME,
                'Key': filename
            },
            ExpiresIn=expiration
        )

        return url

    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

def migrate_from_vercel_blob():
    """
    Migrate existing coverage reports from Vercel Blob to R2

    Returns:
        dict: Migration result with success status and details
    """
    try:
        # This function would need to be implemented if we have access to Vercel Blob
        # For now, it's a placeholder for future migration
        print("Vercel Blob migration not implemented - requires Vercel Blob access")
        return {
            'success': False,
            'error': 'Vercel Blob migration not implemented',
            'migrated_count': 0
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'migrated_count': 0
        }

def validate_coverage_data(coverage_data):
    """
    Validate coverage report data structure

    Args:
        coverage_data (dict): Coverage report data to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        required_fields = [
            'total_lines', 'covered_lines', 'coverage_percentage',
            'uncovered_lines', 'total_branches', 'branches_covered',
            'branch_coverage_percentage', 'files'
        ]

        for field in required_fields:
            if field not in coverage_data:
                print(f"Missing required field: {field}")
                return False

        if not isinstance(coverage_data['files'], dict):
            print("Files field must be a dictionary")
            return False

        return True

    except Exception as e:
        print(f"Error validating coverage data: {e}")
        return False

if __name__ == "__main__":
    # Test the R2 connection
    print("Testing R2 coverage utilities...")

    client = get_r2_client()
    if client:
        print("✅ R2 client created successfully")

        # Test listing reports
        reports = list_coverage_reports(limit=5)
        print(f"Found {len(reports)} coverage reports in R2")

        # Test creating a sample report
        sample_data = {
            'total_lines': 1000,
            'covered_lines': 750,
            'coverage_percentage': 75.0,
            'uncovered_lines': 250,
            'total_branches': 50,
            'branches_covered': 40,
            'branch_coverage_percentage': 80.0,
            'generated_at': datetime.now().isoformat(),
            'files': {
                'test.py': {
                    'total': 100,
                    'covered': 75,
                    'percentage': 75.0,
                    'branches': 10,
                    'branches_covered': 8,
                    'branch_percentage': 80.0
                }
            }
        }

        if validate_coverage_data(sample_data):
            result = upload_coverage_report(sample_data, "test-coverage-report.json")
            if result['success']:
                print(f"✅ Test report uploaded: {result['filename']}")

                # Test downloading
                downloaded = download_coverage_report("test-coverage-report.json")
                if downloaded:
                    print("✅ Test report downloaded successfully")

                # Clean up test file
                if delete_coverage_report("test-coverage-report.json"):
                    print("✅ Test report deleted successfully")
            else:
                print(f"❌ Failed to upload test report: {result['error']}")
        else:
            print("❌ Sample data validation failed")
    else:
        print("❌ R2 client creation failed")
