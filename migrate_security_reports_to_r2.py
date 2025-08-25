#!/usr/bin/env python3
"""
Migrate Security Reports from Vercel Blob to Cloudflare R2

This script migrates existing quality analysis and vulnerability scan reports
from Vercel Blob storage to Cloudflare R2 storage as part of the Vercel Blob cleanup process.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import utils.r2_quality_utils as r2_quality
import utils.r2_vulnerability_utils as r2_vuln

load_dotenv()

def list_vercel_blob_quality_reports():
    """
    List quality analysis reports in Vercel Blob storage

    Returns:
        list: List of quality analysis report metadata from Vercel Blob
    """
    try:
        from vercel_blob import list as blob_list

        print("Fetching quality analysis reports from Vercel Blob...")
        blob_response = blob_list()

        quality_reports = []

        if blob_response and 'blobs' in blob_response:
            for blob in blob_response['blobs']:
                pathname = blob.get('pathname', '')
                if pathname.startswith('reports/quality-analysis_'):
                    quality_reports.append({
                        'pathname': pathname,
                        'url': blob.get('url', ''),
                        'size': blob.get('size', 0),
                        'uploadedAt': blob.get('uploadedAt', '')
                    })

        # Sort by upload date (newest first)
        quality_reports.sort(key=lambda x: x.get('uploadedAt', ''), reverse=True)
        return quality_reports

    except ImportError:
        print("❌ Vercel Blob library not available")
        return []
    except Exception as e:
        print(f"❌ Error listing Vercel Blob quality reports: {e}")
        return []

def list_vercel_blob_vulnerability_reports():
    """
    List vulnerability scan reports in Vercel Blob storage

    Returns:
        list: List of vulnerability scan report metadata from Vercel Blob
    """
    try:
        from vercel_blob import list as blob_list

        print("Fetching vulnerability scan reports from Vercel Blob...")
        blob_response = blob_list()

        vuln_reports = []

        if blob_response and 'blobs' in blob_response:
            for blob in blob_response['blobs']:
                pathname = blob.get('pathname', '')
                if pathname.startswith('reports/vulnerability-scan_'):
                    vuln_reports.append({
                        'pathname': pathname,
                        'url': blob.get('url', ''),
                        'size': blob.get('size', 0),
                        'uploadedAt': blob.get('uploadedAt', '')
                    })

        # Sort by upload date (newest first)
        vuln_reports.sort(key=lambda x: x.get('uploadedAt', ''), reverse=True)
        return vuln_reports

    except ImportError:
        print("❌ Vercel Blob library not available")
        return []
    except Exception as e:
        print(f"❌ Error listing Vercel Blob vulnerability reports: {e}")
        return []

def download_report_from_blob(blob_url):
    """
    Download report content from Vercel Blob

    Args:
        blob_url (str): URL of the report in Vercel Blob

    Returns:
        dict: Report data or None if error
    """
    try:
        response = requests.get(blob_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to download from {blob_url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error downloading report: {e}")
        return None

def migrate_quality_reports():
    """
    Migrate all quality analysis reports from Vercel Blob to R2

    Returns:
        dict: Migration result with success status and details
    """
    print("🔄 Starting quality analysis report migration from Vercel Blob to R2...")

    # Get quality reports from Vercel Blob
    blob_reports = list_vercel_blob_quality_reports()

    if not blob_reports:
        print("ℹ️  No quality analysis reports found in Vercel Blob")
        return {
            'success': True,
            'migrated_count': 0,
            'skipped_count': 0,
            'error_count': 0,
            'details': []
        }

    print(f"📊 Found {len(blob_reports)} quality analysis reports in Vercel Blob")

    migrated_count = 0
    skipped_count = 0
    error_count = 0
    details = []

    for i, blob_report in enumerate(blob_reports, 1):
        pathname = blob_report['pathname']
        blob_url = blob_report['url']

        print(f"\n[{i}/{len(blob_reports)}] Processing: {pathname}")

        try:
            # Download quality data from Vercel Blob
            quality_data = download_report_from_blob(blob_url)

            if not quality_data:
                print(f"❌ Failed to download quality data from {pathname}")
                error_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'error',
                    'error': 'Failed to download from Vercel Blob'
                })
                continue

            # Validate quality data
            if not r2_quality.validate_quality_data(quality_data):
                print(f"❌ Invalid quality data format for {pathname}")
                error_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'error',
                    'error': 'Invalid quality data format'
                })
                continue

            # Check if already exists in R2
            filename = pathname.replace('reports/', '')
            existing_reports = r2_quality.list_quality_reports(limit=100)
            already_exists = any(report['filename'] == pathname for report in existing_reports)

            if already_exists:
                print(f"⏭️  Already exists in R2: {pathname}")
                skipped_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'skipped',
                    'reason': 'Already exists in R2'
                })
                continue

            # Upload to R2
            result = r2_quality.upload_quality_report(quality_data, filename)

            if result['success']:
                print(f"✅ Migrated to R2: {result['filename']}")
                migrated_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'migrated',
                    'r2_filename': result['filename'],
                    'size': result['size']
                })
            else:
                print(f"❌ Failed to upload to R2: {result['error']}")
                error_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'error',
                    'error': result['error']
                })

        except Exception as e:
            print(f"❌ Error processing {pathname}: {e}")
            error_count += 1
            details.append({
                'pathname': pathname,
                'status': 'error',
                'error': str(e)
            })

    # Print summary
    print(f"\n📋 Quality Analysis Migration Summary:")
    print(f"   ✅ Migrated: {migrated_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📊 Total: {len(blob_reports)}")

    return {
        'success': error_count == 0,
        'migrated_count': migrated_count,
        'skipped_count': skipped_count,
        'error_count': error_count,
        'details': details
    }

def migrate_vulnerability_reports():
    """
    Migrate all vulnerability scan reports from Vercel Blob to R2

    Returns:
        dict: Migration result with success status and details
    """
    print("🔄 Starting vulnerability scan report migration from Vercel Blob to R2...")

    # Get vulnerability reports from Vercel Blob
    blob_reports = list_vercel_blob_vulnerability_reports()

    if not blob_reports:
        print("ℹ️  No vulnerability scan reports found in Vercel Blob")
        return {
            'success': True,
            'migrated_count': 0,
            'skipped_count': 0,
            'error_count': 0,
            'details': []
        }

    print(f"📊 Found {len(blob_reports)} vulnerability scan reports in Vercel Blob")

    migrated_count = 0
    skipped_count = 0
    error_count = 0
    details = []

    for i, blob_report in enumerate(blob_reports, 1):
        pathname = blob_report['pathname']
        blob_url = blob_report['url']

        print(f"\n[{i}/{len(blob_reports)}] Processing: {pathname}")

        try:
            # Download vulnerability data from Vercel Blob
            vuln_data = download_report_from_blob(blob_url)

            if not vuln_data:
                print(f"❌ Failed to download vulnerability data from {pathname}")
                error_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'error',
                    'error': 'Failed to download from Vercel Blob'
                })
                continue

            # Validate vulnerability data
            if not r2_vuln.validate_vulnerability_data(vuln_data):
                print(f"❌ Invalid vulnerability data format for {pathname}")
                error_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'error',
                    'error': 'Invalid vulnerability data format'
                })
                continue

            # Check if already exists in R2
            filename = pathname.replace('reports/', '')
            existing_reports = r2_vuln.list_vulnerability_reports(limit=100)
            already_exists = any(report['filename'] == pathname for report in existing_reports)

            if already_exists:
                print(f"⏭️  Already exists in R2: {pathname}")
                skipped_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'skipped',
                    'reason': 'Already exists in R2'
                })
                continue

            # Upload to R2
            result = r2_vuln.upload_vulnerability_report(vuln_data, filename)

            if result['success']:
                print(f"✅ Migrated to R2: {result['filename']}")
                migrated_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'migrated',
                    'r2_filename': result['filename'],
                    'size': result['size']
                })
            else:
                print(f"❌ Failed to upload to R2: {result['error']}")
                error_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'error',
                    'error': result['error']
                })

        except Exception as e:
            print(f"❌ Error processing {pathname}: {e}")
            error_count += 1
            details.append({
                'pathname': pathname,
                'status': 'error',
                'error': str(e)
            })

    # Print summary
    print(f"\n📋 Vulnerability Scan Migration Summary:")
    print(f"   ✅ Migrated: {migrated_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📊 Total: {len(blob_reports)}")

    return {
        'success': error_count == 0,
        'migrated_count': migrated_count,
        'skipped_count': skipped_count,
        'error_count': error_count,
        'details': details
    }

def cleanup_vercel_blob_reports(migrated_reports, report_type):
    """
    Clean up reports from Vercel Blob after successful migration

    Args:
        migrated_reports (list): List of successfully migrated reports
        report_type (str): Type of reports ('quality' or 'vulnerability')

    Returns:
        dict: Cleanup result
    """
    print(f"\n🧹 Starting cleanup of Vercel Blob {report_type} reports...")

    try:
        from vercel_blob import del_

        deleted_count = 0
        error_count = 0

        for report in migrated_reports:
            if report['status'] == 'migrated':
                try:
                    pathname = report['pathname']
                    print(f"🗑️  Deleting from Vercel Blob: {pathname}")

                    # Delete from Vercel Blob
                    del_(pathname)
                    deleted_count += 1

                except Exception as e:
                    print(f"❌ Error deleting {pathname}: {e}")
                    error_count += 1

        print(f"\n📋 {report_type.title()} Cleanup Summary:")
        print(f"   🗑️  Deleted: {deleted_count}")
        print(f"   ❌ Errors: {error_count}")

        return {
            'success': error_count == 0,
            'deleted_count': deleted_count,
            'error_count': error_count
        }

    except ImportError:
        print("❌ Vercel Blob library not available for cleanup")
        return {
            'success': False,
            'error': 'Vercel Blob library not available'
        }
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Main migration function"""
    print("🚀 Security Reports Migration: Vercel Blob → Cloudflare R2")
    print("=" * 60)

    # Check R2 configuration
    print("🔍 Checking R2 configuration...")
    quality_client = r2_quality.get_r2_client()
    vuln_client = r2_vuln.get_r2_client()

    if not quality_client or not vuln_client:
        print("❌ R2 client not available. Please check R2 credentials.")
        return

    print("✅ R2 configuration valid")

    # Perform quality analysis migration
    print("\n" + "="*60)
    quality_result = migrate_quality_reports()

    # Perform vulnerability scan migration
    print("\n" + "="*60)
    vuln_result = migrate_vulnerability_reports()

    # Ask for confirmation before cleanup
    total_migrated = quality_result['migrated_count'] + vuln_result['migrated_count']

    if total_migrated > 0:
        print(f"\n⚠️  {total_migrated} reports were successfully migrated.")
        print("Do you want to delete the original reports from Vercel Blob? (y/N): ", end="")

        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                # Clean up quality reports
                if quality_result['migrated_count'] > 0:
                    quality_migrated = [r for r in quality_result['details'] if r['status'] == 'migrated']
                    quality_cleanup = cleanup_vercel_blob_reports(quality_migrated, 'quality')

                    if quality_cleanup['success']:
                        print("✅ Quality reports cleanup completed successfully")
                    else:
                        print(f"❌ Quality reports cleanup failed: {quality_cleanup.get('error', 'Unknown error')}")

                # Clean up vulnerability reports
                if vuln_result['migrated_count'] > 0:
                    vuln_migrated = [r for r in vuln_result['details'] if r['status'] == 'migrated']
                    vuln_cleanup = cleanup_vercel_blob_reports(vuln_migrated, 'vulnerability')

                    if vuln_cleanup['success']:
                        print("✅ Vulnerability reports cleanup completed successfully")
                    else:
                        print(f"❌ Vulnerability reports cleanup failed: {vuln_cleanup.get('error', 'Unknown error')}")
            else:
                print("⏭️  Skipping cleanup - original reports preserved in Vercel Blob")
        except KeyboardInterrupt:
            print("\n⏭️  Cleanup cancelled by user")

    # Save migration report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"security_reports_migration_report_{timestamp}.json"

    migration_report = {
        'timestamp': datetime.now().isoformat(),
        'quality_analysis': quality_result,
        'vulnerability_scan': vuln_result,
        'total_migrated': total_migrated,
        'total_errors': quality_result['error_count'] + vuln_result['error_count']
    }

    with open(report_filename, 'w') as f:
        json.dump(migration_report, f, indent=2)

    print(f"\n📄 Migration report saved to: {report_filename}")
    print("✅ Migration process completed")

if __name__ == "__main__":
    main()
