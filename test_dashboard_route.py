#!/usr/bin/env python3
"""Test dashboard route to ensure it works after database fix"""

from app import app, db, PotentialRecruit
import traceback

def test_dashboard():
    print("Testing dashboard route...")
    try:
        with app.app_context():
            # Test the specific query that was failing
            print("Testing PotentialRecruit.query.count()...")
            recruit_count = PotentialRecruit.query.count()
            print(f"✅ PotentialRecruit count: {recruit_count}")

            # Test the dashboard route
            with app.test_client() as client:
                print("\nTesting dashboard route...")
                response = client.get('/dashboard')
                print(f"Dashboard status: {response.status_code}")

                if response.status_code == 302:
                    print("✅ Dashboard redirects to login (expected when not authenticated)")
                elif response.status_code == 200:
                    print("✅ Dashboard loads successfully")
                else:
                    print(f"❌ Dashboard failed with status {response.status_code}")

                # Test with authentication
                print("\nTesting dashboard with authentication...")
                with client.session_transaction() as sess:
                    sess['user_id'] = 1
                    sess['username'] = 'admin'
                    sess['role'] = 'admin'

                response = client.get('/dashboard')
                print(f"Authenticated dashboard status: {response.status_code}")

                if response.status_code == 200:
                    print("✅ Authenticated dashboard loads successfully")
                else:
                    print(f"❌ Authenticated dashboard failed with status {response.status_code}")
                    print(f"Response: {response.data[:200]}...")

            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard()
    if success:
        print("\n🎉 Dashboard tests completed!")
    else:
        print("\n💥 Dashboard tests failed!")
