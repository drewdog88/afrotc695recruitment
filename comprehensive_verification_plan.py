#!/usr/bin/env python3
"""
Comprehensive Verification Plan for AFROTC 695 Recruitment System
After Environment Cleanup and 2FA Removal

This script systematically tests all aspects of the application to ensure:
1. Environment variables load correctly
2. Database connections work
3. All routes function properly
4. No 2FA references remain
5. Application starts and runs without errors
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n--- {title} ---")

def check_environment_files():
    """Verify environment file structure is correct"""
    print_section("Environment Files Check")
    
    # Check that .env exists and is the only environment file
    env_files = list(Path('.').glob('.env*'))
    local_env_files = list(Path('.').glob('env*'))
    
    print(f"Found .env* files: {[f.name for f in env_files]}")
    print(f"Found env* files: {[f.name for f in local_env_files]}")
    
    # Should only have .env and env-old directory
    expected_files = ['.env', 'env-old']
    actual_files = [f.name for f in local_env_files if f.is_file()] + [f.name for f in env_files]
    
    if set(actual_files) == set(expected_files):
        print("✅ Environment file structure is correct")
        return True
    else:
        print("❌ Unexpected environment files found")
        print(f"Expected: {expected_files}")
        print(f"Actual: {actual_files}")
        return False

def check_env_content():
    """Verify .env file content is correct"""
    print_section(".env File Content Check")
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Check for required variables
        required_vars = [
            'FLASK_ENV=development',
            'DATABASE_URL=',
            'BLOB_READ_WRITE_TOKEN=',
            'SECRET_KEY=',
            'BCRYPT_ROUNDS='
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required variables: {missing_vars}")
            return False
        
        # Check that TOTP_ENCRYPTION_KEY is NOT present
        if 'TOTP_ENCRYPTION_KEY' in content:
            print("❌ TOTP_ENCRYPTION_KEY still present in .env")
            return False
        
        print("✅ .env file content is correct")
        return True
        
    except FileNotFoundError:
        print("❌ .env file not found")
        return False

def test_environment_loading():
    """Test that environment variables load correctly"""
    print_section("Environment Loading Test")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_env_vars = [
            'FLASK_ENV',
            'DATABASE_URL', 
            'BLOB_READ_WRITE_TOKEN',
            'SECRET_KEY',
            'BCRYPT_ROUNDS'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        
        print("✅ Environment variables load correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print_section("Database Connection Test")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return False
        
        # Parse the URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection successful - PostgreSQL {version[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_app_imports():
    """Test that both app.py and app_local.py import without errors"""
    print_section("Application Import Tests")
    
    # Test app.py
    try:
        print("Testing app.py import...")
        import app
        print("✅ app.py imports successfully")
        app_import_ok = True
    except Exception as e:
        print(f"❌ app.py import failed: {e}")
        app_import_ok = False
    
    # Test app_local.py
    try:
        print("Testing app_local.py import...")
        import app_local
        print("✅ app_local.py imports successfully")
        app_local_import_ok = True
    except Exception as e:
        print(f"❌ app_local.py import failed: {e}")
        app_local_import_ok = False
    
    return app_import_ok and app_local_import_ok

def check_2fa_removal():
    """Verify all 2FA references have been removed"""
    print_section("2FA Removal Verification")
    
    # Files that should not exist
    files_to_check = [
        'utils/2fa_utils.py',
        'templates/setup_2fa.html',
        'templates/verify_2fa.html', 
        'templates/setup_2fa_complete.html',
        'tests/test_user_model_2fa.py',
        'tests/test_database_migration.py'
    ]
    
    existing_2fa_files = []
    for file_path in files_to_check:
        if os.path.exists(file_path):
            existing_2fa_files.append(file_path)
    
    if existing_2fa_files:
        print(f"❌ 2FA files still exist: {existing_2fa_files}")
        return False
    
    # Check for 2FA references in code
    code_files_to_check = [
        'app.py',
        'app_local.py', 
        'api/app.py'
    ]
    
    twofa_keywords = [
        'totp_',
        '2fa',
        'two_factor',
        'backup_codes',
        'TOTP_ENCRYPTION_KEY'
    ]
    
    found_2fa_refs = []
    for file_path in code_files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read().lower()
                    for keyword in twofa_keywords:
                        if keyword in content:
                            found_2fa_refs.append(f"{file_path}: {keyword}")
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
    
    if found_2fa_refs:
        print(f"❌ 2FA references found in code: {found_2fa_refs}")
        return False
    
    print("✅ All 2FA references have been removed")
    return True

def test_flask_app_startup():
    """Test that Flask app can start without errors"""
    print_section("Flask App Startup Test")
    
    try:
        # Test app.py startup
        print("Testing app.py startup...")
        import app
        with app.app.app_context():
            # Test database initialization
            app.db.create_all()
            print("✅ app.py starts successfully and database initializes")
        
        # Test app_local.py startup  
        print("Testing app_local.py startup...")
        import app_local
        with app_local.app.app_context():
            # Test database initialization
            app_local.db.create_all()
            print("✅ app_local.py starts successfully and database initializes")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app startup failed: {e}")
        return False

def test_web_server():
    """Test that the web server can start and respond"""
    print_section("Web Server Test")
    
    try:
        # Start the server in a subprocess
        print("Starting web server...")
        process = subprocess.Popen([
            sys.executable, 'app_local.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get('http://localhost:5000', timeout=5)
            if response.status_code == 200:
                print("✅ Web server responds correctly")
                server_ok = True
            else:
                print(f"❌ Web server returned status {response.status_code}")
                server_ok = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Web server not responding: {e}")
            server_ok = False
        
        # Clean up
        process.terminate()
        process.wait()
        
        return server_ok
        
    except Exception as e:
        print(f"❌ Web server test failed: {e}")
        return False

def run_comprehensive_verification():
    """Run all verification tests"""
    print_header("COMPREHENSIVE VERIFICATION PLAN")
    print("Testing AFROTC 695 Recruitment System after Environment Cleanup and 2FA Removal")
    
    tests = [
        ("Environment Files", check_environment_files),
        ("Environment Content", check_env_content),
        ("Environment Loading", test_environment_loading),
        ("Database Connection", test_database_connection),
        ("App Imports", test_app_imports),
        ("2FA Removal", check_2fa_removal),
        ("Flask Startup", test_flask_app_startup),
        ("Web Server", test_web_server)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The application is ready for use.")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_verification()
    sys.exit(0 if success else 1)
