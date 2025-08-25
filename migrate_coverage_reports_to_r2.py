#!/usr/bin/env python3
"""
Migrate Coverage Reports from Vercel Blob to Cloudflare R2

This script migrates existing code coverage reports from Vercel Blob storage
to Cloudflare R2 storage as part of the Vercel Blob cleanup process.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import utils.r2_coverage_utils as r2_coverage

load_dotenv()

def list_vercel_blob_coverage_reports():
    """
    List coverage reports in Vercel Blob storage

    Returns:
        list: List of coverage report metadata from Vercel Blob
    """
    try:
        from vercel_blob import list as blob_list

        print("Fetching coverage reports from Vercel Blob...")
        blob_response = blob_list()

        coverage_reports = []

        if blob_response and 'blobs' in blob_response:
            for blob in blob_response['blobs']:
                pathname = blob.get('pathname', '')
                if pathname.startswith('reports/coverage-summary_'):
                    coverage_reports.append({
                        'pathname': pathname,
                        'url': blob.get('url', ''),
                        'size': blob.get('size', 0),
                        'uploadedAt': blob.get('uploadedAt', '')
                    })

        # Sort by upload date (newest first)
        coverage_reports.sort(key=lambda x: x.get('uploadedAt', ''), reverse=True)
        return coverage_reports

    except ImportError:
        print("❌ Vercel Blob library not available")
        return []
    except Exception as e:
        print(f"❌ Error listing Vercel Blob coverage reports: {e}")
        return []

def download_coverage_report_from_blob(blob_url):
    """
    Download coverage report content from Vercel Blob

    Args:
        blob_url (str): URL of the coverage report in Vercel Blob

    Returns:
        dict: Coverage report data or None if error
    """
    try:
        response = requests.get(blob_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to download from {blob_url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error downloading coverage report: {e}")
        return None

def migrate_coverage_reports():
    """
    Migrate all coverage reports from Vercel Blob to R2

    Returns:
        dict: Migration result with success status and details
    """
    print("🔄 Starting coverage report migration from Vercel Blob to R2...")

    # Get coverage reports from Vercel Blob
    blob_reports = list_vercel_blob_coverage_reports()

    if not blob_reports:
        print("ℹ️  No coverage reports found in Vercel Blob")
        return {
            'success': True,
            'migrated_count': 0,
            'skipped_count': 0,
            'error_count': 0,
            'details': []
        }

    print(f"📊 Found {len(blob_reports)} coverage reports in Vercel Blob")

    migrated_count = 0
    skipped_count = 0
    error_count = 0
    details = []

    for i, blob_report in enumerate(blob_reports, 1):
        pathname = blob_report['pathname']
        blob_url = blob_report['url']

        print(f"\n[{i}/{len(blob_reports)}] Processing: {pathname}")

        try:
            # Download coverage data from Vercel Blob
            coverage_data = download_coverage_report_from_blob(blob_url)

            if not coverage_data:
                print(f"❌ Failed to download coverage data from {pathname}")
                error_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'error',
                    'error': 'Failed to download from Vercel Blob'
                })
                continue

            # Validate coverage data
            if not r2_coverage.validate_coverage_data(coverage_data):
                print(f"❌ Invalid coverage data format for {pathname}")
                error_count += 1
                details.append({
                    'pathname': pathname,
                    'status': 'error',
                    'error': 'Invalid coverage data format'
                })
                continue

            # Check if already exists in R2
            filename = pathname.replace('reports/', '')
            existing_reports = r2_coverage.list_coverage_reports(limit=100)
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
            result = r2_coverage.upload_coverage_report(coverage_data, filename)

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
    print(f"\n📋 Migration Summary:")
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

def cleanup_vercel_blob_coverage_reports(migrated_reports):
    """
    Clean up coverage reports from Vercel Blob after successful migration

    Args:
        migrated_reports (list): List of successfully migrated reports

    Returns:
        dict: Cleanup result
    """
    print("\n🧹 Starting cleanup of Vercel Blob coverage reports...")

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

        print(f"\n📋 Cleanup Summary:")
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
    print("🚀 Coverage Report Migration: Vercel Blob → Cloudflare R2")
    print("=" * 60)

    # Check R2 configuration
    print("🔍 Checking R2 configuration...")
    r2_client = r2_coverage.get_r2_client()
    if not r2_client:
        print("❌ R2 client not available. Please check R2 credentials.")
        return

    print("✅ R2 configuration valid")

    # Perform migration
    migration_result = migrate_coverage_reports()

    if migration_result['success'] and migration_result['migrated_count'] > 0:
        # Ask for confirmation before cleanup
        print(f"\n⚠️  {migration_result['migrated_count']} reports were successfully migrated.")
        print("Do you want to delete the original reports from Vercel Blob? (y/N): ", end="")

        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                migrated_reports = [r for r in migration_result['details'] if r['status'] == 'migrated']
                cleanup_result = cleanup_vercel_blob_coverage_reports(migrated_reports)

                if cleanup_result['success']:
                    print("✅ Cleanup completed successfully")
                else:
                    print(f"❌ Cleanup failed: {cleanup_result.get('error', 'Unknown error')}")
            else:
                print("⏭️  Skipping cleanup - original reports preserved in Vercel Blob")
        except KeyboardInterrupt:
            print("\n⏭️  Cleanup cancelled by user")

    # Save migration report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"coverage_migration_report_{timestamp}.json"

    with open(report_filename, 'w') as f:
        json.dump(migration_result, f, indent=2)

    print(f"\n📄 Migration report saved to: {report_filename}")
    print("✅ Migration process completed")

if __name__ == "__main__":
    main()
