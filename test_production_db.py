#!/usr/bin/env python3
"""
Test production database connection to identify serverless function crash
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import time

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection with timeout"""
    print("=== Testing Production Database Connection ===")

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return False

    # Convert postgres:// to postgresql:// for psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print(f"Database URL: {database_url[:50]}...")

    try:
        # Test connection with timeout
        start_time = time.time()
        conn = psycopg2.connect(database_url, connect_timeout=10)
        connection_time = time.time() - start_time

        print(f"✓ Database connection successful in {connection_time:.2f} seconds")

        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cadet")
        cadet_count = cursor.fetchone()[0]

        print(f"✓ Query successful - {cadet_count} cadets found")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("\n=== Testing Environment Variables ===")

    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    optional_vars = ['BLOB_READ_WRITE_TOKEN']

    all_good = True

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: Set (length: {len(value)})")
        else:
            print(f"❌ {var}: Missing")
            all_good = False

    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: Set (length: {len(value)})")
        else:
            print(f"⚠ {var}: Not set (optional)")

    return all_good

def test_flask_imports():
    """Test if all Flask imports work"""
    print("\n=== Testing Flask Imports ===")

    try:
        from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
        from flask_sqlalchemy import SQLAlchemy
        from werkzeug.security import generate_password_hash, check_password_hash
        from datetime import datetime, date, time, timezone, timedelta
        from dotenv import load_dotenv
        from sqlalchemy.pool import NullPool
        from sqlalchemy import text

        print("✓ All Flask imports successful")
        return True

    except Exception as e:
        print(f"❌ Flask import error: {e}")
        return False

def main():
    """Main test function"""
    print("=== Production Environment Test ===")

    # Test environment variables
    if not test_environment_variables():
        print("\n❌ Environment variables test failed")
        return

    # Test Flask imports
    if not test_flask_imports():
        print("\n❌ Flask imports test failed")
        return

    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection test failed")
        print("\nPossible causes of serverless function crash:")
        print("1. Database connection timeout")
        print("2. Missing environment variables")
        print("3. Database credentials issue")
        print("4. Network connectivity issue")
        return

    print("\n✅ All tests passed!")
    print("If the serverless function is still crashing, the issue might be:")
    print("1. Vercel deployment needs to be redeployed")
    print("2. Environment variables not set in Vercel dashboard")
    print("3. Database connection pooling issue in serverless environment")
    print("4. Memory/timeout limits exceeded")

if __name__ == "__main__":
    main()
