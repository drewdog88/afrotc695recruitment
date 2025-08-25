#!/usr/bin/env python3
"""
Comprehensive test runner for AFROTC 695 Recruitment Management System.
Runs all test suites and provides detailed coverage reporting.
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

# Load test environment variables
if os.path.exists('.env.test'):
    load_dotenv('.env.test')


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def check_environment():
    """Check if required environment variables are set."""
    print_section("Environment Check")

    required_vars = [
        'TEST_DATABASE_URL',
        'SECRET_KEY'
    ]

    optional_vars = [
        'BLOB_READ_WRITE_TOKEN',
        'CLOUDFLARE_R2_ACCESS_KEY_ID',
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
        'CLOUDFLARE_R2_ACCOUNT_ID',
        'CLOUDFLARE_R2_BUCKET_NAME'
    ]

    missing_required = []
    missing_optional = []

    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)

    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)

    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please set these variables before running tests.")
        return False

    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {', '.join(missing_optional)}")
        print("Some tests may be skipped.")

    print("✅ Environment check completed")
    return True


def run_command(command, description, capture_output=True):
    """Run a command and return the result."""
    print(f"\n🔄 {description}...")
    start_time = time.time()

    try:
        if capture_output:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                timeout=300
            )

        elapsed_time = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ {description} completed in {elapsed_time:.2f}s")
            return result
        else:
            print(f"❌ {description} failed after {elapsed_time:.2f}s")
            if capture_output and result.stderr:
                print(f"Error: {result.stderr}")
            return result

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 5 minutes")
        return None
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return None


def run_storage_tests():
    """Run storage-specific tests."""
    print_section("Storage Tests")

    # Run Vercel Blob tests
    result = run_command(
        "python -m pytest tests/storage/test_vercel_blob.py -v --tb=short",
        "Vercel Blob Storage Tests"
    )

    # Run Cloudflare R2 tests
    result2 = run_command(
        "python -m pytest tests/storage/test_cloudflare_r2.py -v --tb=short",
        "Cloudflare R2 Storage Tests"
    )

    # Run storage integration tests
    result3 = run_command(
        "python -m pytest tests/integration/test_storage_integration.py -v --tb=short",
        "Storage Integration Tests"
    )

    return all(r and r.returncode == 0 for r in [result, result2, result3])


def run_authentication_tests():
    """Run authentication and authorization tests."""
    print_section("Authentication & Authorization Tests")

    result = run_command(
        "python -m pytest tests/unit/test_auth.py -v --tb=short",
        "Authentication Unit Tests"
    )

    return result and result.returncode == 0


def run_recruit_management_tests():
    """Run recruit management tests."""
    print_section("Recruit Management Tests")

    result = run_command(
        "python -m pytest tests/unit/test_recruit_management.py -v --tb=short",
        "Recruit Management Unit Tests"
    )

    return result and result.returncode == 0


def run_all_unit_tests():
    """Run all unit tests."""
    print_section("All Unit Tests")

    result = run_command(
        "python -m pytest tests/unit/ -v --tb=short",
        "All Unit Tests"
    )

    return result and result.returncode == 0


def run_all_integration_tests():
    """Run all integration tests."""
    print_section("All Integration Tests")

    result = run_command(
        "python -m pytest tests/integration/ -v --tb=short",
        "All Integration Tests"
    )

    return result and result.returncode == 0


def run_coverage_analysis():
    """Run comprehensive coverage analysis."""
    print_section("Coverage Analysis")

    # Run tests with coverage
    result = run_command(
        "python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=html --cov-report=json",
        "Coverage Analysis"
    )

    if result and result.returncode == 0:
        # Extract coverage percentage from output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                print(f"📊 Coverage Summary: {line.strip()}")
                break

    return result and result.returncode == 0


def run_specific_test_suite(suite_name):
    """Run a specific test suite."""
    suites = {
        'storage': run_storage_tests,
        'auth': run_authentication_tests,
        'recruit': run_recruit_management_tests,
        'unit': run_all_unit_tests,
        'integration': run_all_integration_tests,
        'coverage': run_coverage_analysis
    }

    if suite_name in suites:
        return suites[suite_name]()
    else:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(suites.keys())}")
        return False


def generate_test_report():
    """Generate a comprehensive test report."""
    print_section("Test Report Generation")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.txt"

    # Run tests and capture output
    result = run_command(
        f"python -m pytest tests/ -v --tb=short > {report_file} 2>&1",
        "Generating Test Report",
        capture_output=False
    )

    if result and result.returncode == 0:
        print(f"📄 Test report saved to: {report_file}")
        return True
    else:
        print("❌ Failed to generate test report")
        return False


def main():
    """Main function to run comprehensive tests."""
    print_header("AFROTC 695 Recruitment Management System - Comprehensive Test Suite")

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) > 1:
        suite = sys.argv[1].lower()
        if suite == 'report':
            generate_test_report()
            return
        elif suite == 'coverage':
            run_coverage_analysis()
            return
        else:
            success = run_specific_test_suite(suite)
            sys.exit(0 if success else 1)

    # Run all tests
    print_section("Running All Tests")

    test_results = {
        'Storage Tests': run_storage_tests(),
        'Authentication Tests': run_authentication_tests(),
        'Recruit Management Tests': run_recruit_management_tests(),
        'All Unit Tests': run_all_unit_tests(),
        'All Integration Tests': run_all_integration_tests(),
        'Coverage Analysis': run_coverage_analysis()
    }

    # Print summary
    print_header("Test Results Summary")

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} test suites passed")

    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
