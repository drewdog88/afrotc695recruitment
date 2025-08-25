#!/usr/bin/env python3
"""
Test Environment Setup Script
Sets up environment variables for testing the AFROTC 695 Recruitment Management System
"""

import os
import sys
from pathlib import Path

def setup_test_environment():
    """Set up test environment variables"""
    print("🔧 Setting up test environment...")

    # Test database URL (using SQLite for testing)
    test_db_url = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')

    # Set test environment variables
    env_vars = {
        'TEST_DATABASE_URL': test_db_url,
        'SECRET_KEY': 'test-secret-key-for-testing-only',
        'FLASK_ENV': 'testing',
        'TESTING': 'true',
        'WTF_CSRF_ENABLED': 'false',
        'VERCEL_BLOB_ENABLED': 'true',
        'CLOUDFLARE_R2_ENABLED': 'true'
    }

    # Check if we have actual credentials to use
    blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
    if blob_token:
        env_vars['BLOB_READ_WRITE_TOKEN'] = blob_token
        print("✅ Using existing BLOB_READ_WRITE_TOKEN")
    else:
        print("⚠️  BLOB_READ_WRITE_TOKEN not found - tests will use mocks")

    # Check Cloudflare R2 credentials
    r2_credentials = [
        'CLOUDFLARE_R2_ACCESS_KEY_ID',
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
        'CLOUDFLARE_R2_ACCOUNT_ID',
        'CLOUDFLARE_R2_BUCKET_NAME'
    ]

    r2_configured = True
    for cred in r2_credentials:
        value = os.getenv(cred)
        if value:
            env_vars[cred] = value
        else:
            r2_configured = False
            print(f"⚠️  {cred} not found")

    if r2_configured:
        print("✅ Using existing Cloudflare R2 credentials")
    else:
        print("⚠️  Cloudflare R2 credentials not fully configured - R2 tests will be skipped")

    # Create .env.test file
    env_file = Path('.env.test')
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    print(f"✅ Created {env_file} with test environment variables")

    # Create test database directory
    test_db_dir = Path('test_db')
    test_db_dir.mkdir(exist_ok=True)
    print(f"✅ Created test database directory: {test_db_dir}")

    return env_vars

def check_dependencies():
    """Check if required testing dependencies are installed"""
    print("\n📦 Checking testing dependencies...")

    required_packages = [
        'pytest',
        'pytest-flask',
        'pytest-cov',
        'pytest-mock',
        'factory-boy',
        'faker'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            if package == 'factory-boy':
                __import__('factory')
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False

    print("✅ All testing dependencies are installed")
    return True

def create_test_directories():
    """Create necessary test directories"""
    print("\n📁 Creating test directories...")

    directories = [
        'tests',
        'tests/storage',
        'tests/integration',
        'tests/unit',
        'tests/fixtures',
        'tests/mocks',
        'coverage_reports',
        'coverage_reports/html'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

    # Create __init__.py files if they don't exist
    init_files = [
        'tests/__init__.py',
        'tests/storage/__init__.py',
        'tests/integration/__init__.py',
        'tests/unit/__init__.py'
    ]

    for init_file in init_files:
        if not Path(init_file).exists():
            Path(init_file).touch()
            print(f"✅ Created {init_file}")

def main():
    """Main setup function"""
    print("🧪 AFROTC 695 Test Environment Setup")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before continuing")
        sys.exit(1)

    # Create directories
    create_test_directories()

    # Setup environment
    env_vars = setup_test_environment()

    print("\n" + "=" * 50)
    print("✅ Test environment setup completed!")
    print("\nNext steps:")
    print("1. Run tests: python run_simple_storage_tests.py")
    print("2. Run full test suite: python run_storage_tests.py")
    print("3. Run specific tests: python -m pytest tests/storage/")
    print("4. View coverage: open coverage_reports/html/index.html")

    print("\nEnvironment variables set:")
    for key, value in env_vars.items():
        if 'SECRET' in key or 'KEY' in key or 'TOKEN' in key:
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
