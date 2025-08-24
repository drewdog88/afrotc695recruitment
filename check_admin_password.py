#!/usr/bin/env python3
"""
Script to check the admin user's password hash in the database
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

def check_admin_password():
    """Check the admin user's password hash field in the database"""

    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print(f"Database URL: {database_url}")

    try:
        # Create engine
        engine = create_engine(database_url)

        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()

        # First, let's see what tables exist
        print("\n=== AVAILABLE TABLES ===")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(f"Table: {table}")

        # Check user table schema (it might be named 'user' not 'users')
        print("\n=== USER TABLE SCHEMA ===")
        try:
            columns = inspector.get_columns('user')
            for column in columns:
                print(f"Column: {column['name']}, Type: {column['type']}, Nullable: {column['nullable']}")
        except Exception as e:
            print(f"Error getting user table schema: {e}")

        # Check admin user's password hash
        print("\n=== ADMIN USER PASSWORD HASH ===")
        result = session.execute(text("SELECT username, password_hash FROM \"user\" WHERE username = 'admin'"))
        admin_user = result.fetchone()

        if admin_user:
            username, password_hash = admin_user
            print(f"Username: {username}")
            print(f"Password hash: {password_hash}")
            print(f"Password hash length: {len(password_hash) if password_hash else 0}")
            print(f"Password hash starts with '$2b$': {password_hash.startswith('$2b$') if password_hash else False}")
            print(f"Password hash starts with '$2a$': {password_hash.startswith('$2a$') if password_hash else False}")
            print(f"Password hash starts with '$2y$': {password_hash.startswith('$2y$') if password_hash else False}")

            # Check if it looks like a hash
            if password_hash and (password_hash.startswith('$2b$') or password_hash.startswith('$2a$') or password_hash.startswith('$2y$')):
                print("✅ Password appears to be properly hashed (bcrypt)")
            elif password_hash and len(password_hash) > 20:
                print("✅ Password appears to be hashed (long string)")
            else:
                print("❌ WARNING: Password appears to be stored in plain text!")
        else:
            print("❌ Admin user not found in database")

        # Check all users for comparison
        print("\n=== ALL USERS PASSWORD STATUS ===")
        result = session.execute(text("SELECT username, password_hash FROM \"user\" LIMIT 5"))
        users = result.fetchall()

        for user in users:
            username, password_hash = user
            is_hashed = password_hash and (password_hash.startswith('$2b$') or password_hash.startswith('$2a$') or password_hash.startswith('$2y$') or len(password_hash) > 20)
            status = "✅ Hashed" if is_hashed else "❌ Plain text"
            print(f"{username}: {status} (length: {len(password_hash) if password_hash else 0})")

        session.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_admin_password()
