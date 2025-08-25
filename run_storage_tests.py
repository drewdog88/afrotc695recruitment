#!/usr/bin/env python3
"""
Storage Test Runner
Runs comprehensive storage tests for Vercel Blob and Cloudflare R2
"""

import os
import sys
import subprocess
from pathlib import Path

def run_storage_tests():
    """Run storage-specific tests"""
    print("🧪 AFROTC 695 Storage Testing Suite")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("tests").exists():
        print("❌ Error: tests directory not found. Run this from the project root.")
        return False

    # Check environment variables
    print("\n📋 Checking storage environment configuration...")

    # Vercel Blob environment
    blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
    if blob_token:
        print("✅ Vercel Blob: BLOB_READ_WRITE_TOKEN configured")
    else:
        print("⚠️  Vercel Blob: BLOB_READ_WRITE_TOKEN not set")

    # Cloudflare R2 environment
    r2_access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
    r2_secret_key = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
    r2_account_id = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
    r2_bucket = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')

    if all([r2_access_key, r2_secret_key, r2_account_id, r2_bucket]):
        print("✅ Cloudflare R2: All credentials configured")
    else:
        print("⚠️  Cloudflare R2: Some credentials missing")
        missing = []
        if not r2_access_key: missing.append("CLOUDFLARE_R2_ACCESS_KEY_ID")
        if not r2_secret_key: missing.append("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
        if not r2_account_id: missing.append("CLOUDFLARE_R2_ACCOUNT_ID")
        if not r2_bucket: missing.append("CLOUDFLARE_R2_BUCKET_NAME")
        print(f"   Missing: {', '.join(missing)}")

    print("\n🚀 Running storage tests...")

    # Run Vercel Blob tests
    print("\n📁 Testing Vercel Blob Storage...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/storage/test_vercel_blob.py",
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("✅ Vercel Blob tests passed")
        else:
            print("❌ Vercel Blob tests failed")
            print(result.stdout)
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⏰ Vercel Blob tests timed out")
    except Exception as e:
        print(f"❌ Error running Vercel Blob tests: {e}")

    # Run Cloudflare R2 tests
    print("\n☁️  Testing Cloudflare R2 Storage...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/storage/test_cloudflare_r2.py",
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("✅ Cloudflare R2 tests passed")
        else:
            print("❌ Cloudflare R2 tests failed")
            print(result.stdout)
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⏰ Cloudflare R2 tests timed out")
    except Exception as e:
        print(f"❌ Error running Cloudflare R2 tests: {e}")

    # Run integration tests
    print("\n🔗 Testing Storage Integration...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/integration/test_storage_integration.py",
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("✅ Storage integration tests passed")
        else:
            print("❌ Storage integration tests failed")
            print(result.stdout)
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⏰ Storage integration tests timed out")
    except Exception as e:
        print(f"❌ Error running storage integration tests: {e}")

    # Run all storage tests together
    print("\n🎯 Running All Storage Tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/storage/", "tests/integration/test_storage_integration.py",
            "-v", "--tb=short", "--cov=app", "--cov-report=term-missing"
        ], capture_output=True, text=True, timeout=600)

        print("\n📊 Test Results:")
        print(result.stdout)

        if result.returncode == 0:
            print("\n🎉 All storage tests completed successfully!")
            return True
        else:
            print("\n❌ Some storage tests failed")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Storage tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running storage tests: {e}")
        return False

def main():
    """Main function"""
    success = run_storage_tests()

    print("\n" + "=" * 50)
    if success:
        print("✅ Storage testing completed successfully!")
        print("\nNext steps:")
        print("1. Review test coverage report")
        print("2. Check for any failed tests")
        print("3. Verify storage operations in production")
    else:
        print("❌ Storage testing encountered issues")
        print("\nTroubleshooting:")
        print("1. Check environment variables")
        print("2. Verify storage credentials")
        print("3. Check network connectivity")
        print("4. Review test logs for specific errors")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
