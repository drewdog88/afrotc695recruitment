#!/usr/bin/env python3
"""
R2 Quality Analysis Report Utilities

This module provides utility functions for managing quality analysis reports
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
    """Get R2 client for quality analysis report operations"""
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

def upload_quality_report(quality_data, filename=None):
    """
    Upload quality analysis report to R2 storage
    
    Args:
        quality_data (dict): Quality analysis report data
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
            filename = f"reports/quality-analysis_{timestamp}.json"
        
        # Ensure reports prefix
        if not filename.startswith('reports/'):
            filename = f"reports/{filename}"
        
        # Convert quality data to JSON
        quality_json = json.dumps(quality_data, indent=2)
        
        # Upload to R2
        response = r2_client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=filename,
            Body=quality_json.encode('utf-8'),
            ContentType='application/json',
            Metadata={
                'uploaded_at': datetime.now().isoformat(),
                'report_type': 'quality_analysis',
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
            'size': len(quality_json),
            'etag': response.get('ETag', '').strip('"'),
            'uploaded_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def list_quality_reports(limit=10):
    """
    List quality analysis reports in R2 storage
    
    Args:
        limit (int): Maximum number of reports to return
    
    Returns:
        list: List of quality analysis report metadata
    """
    try:
        r2_client = get_r2_client()
        if not r2_client:
            return []
        
        response = r2_client.list_objects_v2(
            Bucket=R2_BUCKET_NAME,
            Prefix='reports/quality-analysis_',
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
        print(f"Error listing quality reports: {e}")
        return []

def get_latest_quality_report():
    """
    Get the most recent quality analysis report from R2
    
    Returns:
        dict: Quality analysis report data or None if not found
    """
    try:
        reports = list_quality_reports(limit=1)
        if not reports:
            return None
        
        latest_report = reports[0]
        return download_quality_report(latest_report['filename'])
        
    except Exception as e:
        print(f"Error getting latest quality report: {e}")
        return None

def download_quality_report(filename):
    """
    Download quality analysis report from R2
    
    Args:
        filename (str): Name of the quality analysis report file
    
    Returns:
        dict: Quality analysis report data or None if not found
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
            print(f"Quality report not found: {filename}")
        else:
            print(f"Error downloading quality report: {e}")
        return None
    except Exception as e:
        print(f"Error downloading quality report: {e}")
        return None

def delete_quality_report(filename):
    """
    Delete quality analysis report from R2
    
    Args:
        filename (str): Name of the quality analysis report file
    
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
        print(f"Error deleting quality report: {e}")
        return False

def generate_presigned_url(filename, expiration=3600):
    """
    Generate presigned URL for quality analysis report download
    
    Args:
        filename (str): Name of the quality analysis report file
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
    Migrate existing quality analysis reports from Vercel Blob to R2
    
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

def validate_quality_data(quality_data):
    """
    Validate quality analysis report data structure
    
    Args:
        quality_data (dict): Quality analysis report data to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        required_fields = [
            'code_quality_score', 'test_coverage', 'security_score',
            'performance_score', 'generated_at'
        ]
        
        for field in required_fields:
            if field not in quality_data:
                print(f"Missing required field: {field}")
                return False
        
        # Validate score ranges
        scores = ['code_quality_score', 'test_coverage', 'security_score', 'performance_score']
        for score in scores:
            if not isinstance(quality_data[score], (int, float)) or quality_data[score] < 0 or quality_data[score] > 100:
                print(f"Invalid score value for {score}: {quality_data[score]}")
                return False
        
        return True
        
    except Exception as e:
        print(f"Error validating quality data: {e}")
        return False

if __name__ == "__main__":
    # Test the R2 connection
    print("Testing R2 quality analysis utilities...")
    
    client = get_r2_client()
    if client:
        print("✅ R2 client created successfully")
        
        # Test listing reports
        reports = list_quality_reports(limit=5)
        print(f"Found {len(reports)} quality reports in R2")
        
        # Test creating a sample report
        sample_data = {
            'code_quality_score': 85,
            'test_coverage': 75,
            'security_score': 90,
            'performance_score': 88,
            'generated_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        if validate_quality_data(sample_data):
            result = upload_quality_report(sample_data, "test-quality-report.json")
            if result['success']:
                print(f"✅ Test report uploaded: {result['filename']}")
                
                # Test downloading
                downloaded = download_quality_report("test-quality-report.json")
                if downloaded:
                    print("✅ Test report downloaded successfully")
                
                # Clean up test file
                if delete_quality_report("test-quality-report.json"):
                    print("✅ Test report deleted successfully")
            else:
                print(f"❌ Failed to upload test report: {result['error']}")
        else:
            print("❌ Sample data validation failed")
    else:
        print("❌ R2 client creation failed")
