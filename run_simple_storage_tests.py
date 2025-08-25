#!/usr/bin/env python3
"""
Simple Storage Test Runner
Runs basic storage tests with better error handling and simplified setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")

    # Check Vercel Blob
    blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
    if not blob_token:
        print("⚠️  BLOB_READ_WRITE_TOKEN not set - Vercel Blob tests may fail")
    else:
        print("✅ BLOB_READ_WRITE_TOKEN is set")

    # Check Cloudflare R2
    r2_access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
    r2_secret_key = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
    r2_account_id = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
    r2_bucket = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')

    if not all([r2_access_key, r2_secret_key, r2_account_id, r2_bucket]):
        print("⚠️  Cloudflare R2 credentials not fully configured - R2 tests will be skipped")
    else:
        print("✅ Cloudflare R2 credentials are set")

    # Check test database
    test_db_url = os.getenv('TEST_DATABASE_URL')
    if not test_db_url:
        print("⚠️  TEST_DATABASE_URL not set - using default test database")
    else:
        print("✅ TEST_DATABASE_URL is set")

def run_basic_tests():
    """Run basic storage tests with simplified setup"""
    print("\n🧪 Running basic storage tests...")

    # Test 1: Environment configuration
    print("\n1️⃣ Testing environment configuration...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/storage/test_vercel_blob.py::TestVercelBlobStorage::test_vercel_blob_environment_configuration',
        '-v', '--tb=short'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Environment configuration test passed")
    else:
        print("❌ Environment configuration test failed")
        print(result.stdout)
        print(result.stderr)

    # Test 2: Basic document download
    print("\n2️⃣ Testing basic document download...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/storage/test_vercel_blob.py::TestVercelBlobStorage::test_document_download_workflow',
        '-v', '--tb=short'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Document download test passed")
    else:
        print("❌ Document download test failed")
        print(result.stdout)
        print(result.stderr)

    # Test 3: R2 environment check (skip if not configured)
    print("\n3️⃣ Testing R2 environment configuration...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/storage/test_cloudflare_r2.py::TestCloudflareR2Storage::test_r2_environment_configuration',
        '-v', '--tb=short'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ R2 environment configuration test passed")
    else:
        print("⚠️  R2 environment configuration test failed (likely skipped due to missing credentials)")
        print(result.stdout)

    # Test 4: R2 metadata handling
    print("\n4️⃣ Testing R2 metadata handling...")
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/storage/test_cloudflare_r2.py::TestCloudflareR2Storage::test_backup_metadata_handling',
        '-v', '--tb=short'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ R2 metadata handling test passed")
    else:
        print("❌ R2 metadata handling test failed")
        print(result.stdout)
        print(result.stderr)

def run_coverage_test():
    """Run a simple coverage test"""
    print("\n📊 Running coverage test...")

    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/storage/',
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html:coverage_reports/html',
        '-v',
        '--tb=short'
    ], capture_output=True, text=True)

    print("Coverage test completed")
    if result.returncode == 0:
        print("✅ Coverage test passed")
    else:
        print("⚠️  Coverage test had issues (some tests may have failed)")

    # Show coverage summary
    if "TOTAL" in result.stdout:
        lines = result.stdout.split('\n')
        for line in lines:
            if "TOTAL" in line:
                print(f"📈 {line.strip()}")
                break

def main():
    """Main function"""
    print("🧪 AFROTC 695 Simple Storage Testing")
    print("=" * 50)

    # Check environment
    check_environment()

    # Run basic tests
    run_basic_tests()

    # Run coverage test
    run_coverage_test()

    print("\n" + "=" * 50)
    print("✅ Simple storage testing completed!")
    print("\nNext steps:")
    print("1. Review test results above")
    print("2. Check coverage report in coverage_reports/html/")
    print("3. Fix any failing tests")
    print("4. Run full test suite when basic tests pass")

if __name__ == "__main__":
    main()
