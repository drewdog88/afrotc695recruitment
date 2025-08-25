#!/usr/bin/env python3
"""Test login route and user authentication"""

from app import app, db, User
from werkzeug.security import generate_password_hash
import traceback

def test_login_route():
    print("Testing login route...")
    try:
        with app.app_context():
            # Check if there are any users
            users = User.query.all()
            print(f"Found {len(users)} users in database")

            if len(users) == 0:
                print("⚠️  No users found - this might be the issue!")
                print("Creating a test admin user...")

                # Create a test admin user
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    first_name='Admin',
                    last_name='User',
                    email='admin@example.com',
                    role='admin',
                    secret_question='What is your favorite color?',
                    secret_answer_hash=generate_password_hash('blue')
                )

                db.session.add(admin_user)
                db.session.commit()
                print("✅ Test admin user created")
                print("Username: admin")
                print("Password: admin123")
            else:
                print("Users found:")
                for user in users:
                    print(f"  - {user.username} ({user.role})")

            # Test the login route
            with app.test_client() as client:
                print("\nTesting login route...")
                response = client.get('/login')
                print(f"Login page status: {response.status_code}")

                if response.status_code == 200:
                    print("✅ Login page loads successfully")
                else:
                    print(f"❌ Login page failed with status {response.status_code}")

                # Test dashboard route (should redirect to login)
                response = client.get('/dashboard')
                print(f"Dashboard redirect status: {response.status_code}")

            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_login_route()
    if success:
        print("\n🎉 Login route tests completed!")
    else:
        print("\n💥 Login route tests failed!")
