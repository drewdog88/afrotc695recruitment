#!/usr/bin/env python3
"""
Test script to verify all imports work correctly for production deployment
This helps identify missing dependencies or import issues
"""

import sys
import os

def test_imports():
    """Test all critical imports used by the application"""
    print("Testing critical imports...")

    # Core Flask imports
    try:
        from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
        print("✅ Flask imports successful")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False

    # Database imports
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("✅ SQLAlchemy import successful")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False

    # Security imports
    try:
        from werkzeug.security import generate_password_hash, check_password_hash
        print("✅ Werkzeug security imports successful")
    except ImportError as e:
        print(f"❌ Werkzeug security import failed: {e}")
        return False

    # Environment imports
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv import successful")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False

    # Database driver
    try:
        import psycopg2
        print("✅ psycopg2 import successful")
    except ImportError as e:
        print(f"❌ psycopg2 import failed: {e}")
        return False

    # Authentication
    try:
        import bcrypt
        print("✅ bcrypt import successful")
    except ImportError as e:
        print(f"❌ bcrypt import failed: {e}")
        return False

    # Optional imports (should not fail the app)
    try:
        import pyotp
        print("✅ pyotp import successful")
    except ImportError as e:
        print(f"⚠️ pyotp import failed (optional): {e}")

    try:
        import qrcode
        print("✅ qrcode import successful")
    except ImportError as e:
        print(f"⚠️ qrcode import failed (optional): {e}")

    # Storage imports
    try:
        import boto3
        print("✅ boto3 import successful")
    except ImportError as e:
        print(f"❌ boto3 import failed: {e}")
        return False

    try:
        from vercel_blob import put, list as blob_list, delete, head
        print("✅ vercel-blob import successful")
    except ImportError as e:
        print(f"❌ vercel-blob import failed: {e}")
        return False

    # Export functionality
    try:
        import xlsxwriter
        print("✅ xlsxwriter import successful")
    except ImportError as e:
        print(f"⚠️ xlsxwriter import failed (optional): {e}")

    try:
        from fpdf import FPDF
        print("✅ fpdf2 import successful")
    except ImportError as e:
        print(f"⚠️ fpdf2 import failed (optional): {e}")

    return True

def test_app_creation():
    """Test if the Flask app can be created successfully"""
    print("\nTesting Flask app creation...")

    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()

        # Create Flask app
        from flask import Flask
        app = Flask(__name__)

        # Configure database
        database_url = os.getenv('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'test-key')

        print("✅ Flask app configuration successful")
        print(f"   Database URL: {'SET' if database_url else 'NOT SET'}")
        print(f"   Secret Key: {'SET' if app.config['SECRET_KEY'] != 'test-key' else 'NOT SET'}")

        return True

    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")

    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from dotenv import load_dotenv
        import os

        load_dotenv()

        app = Flask(__name__)
        database_url = os.getenv('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db = SQLAlchemy(app)

        with app.app_context():
            # Test connection
            db.engine.execute("SELECT 1")
            print("✅ Database connection successful")

            # Test table access
            tables = db.engine.table_names()
            print(f"✅ Database tables accessible: {len(tables)} tables found")

        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== Production Import Test ===")

    # Test imports
    imports_ok = test_imports()

    # Test app creation
    app_ok = test_app_creation()

    # Test database connection
    db_ok = test_database_connection()

    print("\n=== Test Results ===")
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"App Creation: {'✅ PASS' if app_ok else '❌ FAIL'}")
    print(f"Database: {'✅ PASS' if db_ok else '❌ FAIL'}")

    if imports_ok and app_ok and db_ok:
        print("\n🎉 All tests passed! The application should work in production.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
