#!/usr/bin/env python3
"""Test database connection and app startup"""

from app import app, db
import traceback

def test_app_startup():
    print("Testing app startup...")
    try:
        with app.app_context():
            print("✅ App context created successfully")

            # Test database connection
            print("Testing database connection...")
            db.create_all()
            print("✅ Database connection successful")

            # Test basic query
            from app import User
            user_count = User.query.count()
            print(f"✅ User count: {user_count}")

            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
