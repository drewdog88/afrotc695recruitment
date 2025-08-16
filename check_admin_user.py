#!/usr/bin/env python3
"""
Check admin user details and verify login credentials
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get connection to production database"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    # Convert postgres:// to postgresql:// for psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def main():
    """Check admin user details"""
    print("=== Admin User Details Check ===")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Check admin user
    cursor.execute('SELECT id, username, email, first_name, last_name, role, is_active, is_locked FROM "user" WHERE username = %s', ('admin',))
    user = cursor.fetchone()
    
    if user:
        print(f"✓ Admin user found:")
        print(f"  ID: {user[0]}")
        print(f"  Username: {user[1]}")
        print(f"  Email: {user[2]}")
        print(f"  First Name: {user[3]}")
        print(f"  Last Name: {user[4]}")
        print(f"  Role: {user[5]}")
        print(f"  Is Active: {user[6]}")
        print(f"  Is Locked: {user[7]}")
        
        # Check if user is locked
        if user[7]:
            print("⚠ WARNING: Admin user is LOCKED!")
            print("   This would prevent login.")
        else:
            print("✓ Admin user is not locked")
            
        # Check if user is active
        if user[6]:
            print("✓ Admin user is active")
        else:
            print("⚠ WARNING: Admin user is INACTIVE!")
            print("   This would prevent login.")
            
    else:
        print("❌ Admin user not found!")
        print("   This would prevent login.")
    
    cursor.close()
    conn.close()
    
    print("\n=== Login Credentials ===")
    print("Username: admin")
    print("Password: admin123")
    print("\nIf login still fails, try:")
    print("1. Check if the Flask app is running")
    print("2. Clear browser cache/cookies")
    print("3. Try a different browser")

if __name__ == "__main__":
    main()
