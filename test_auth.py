#!/usr/bin/env python3
from app import app, User
from flask import session
import requests

def test_auth():
    with app.app_context():
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print(f"✅ Admin user exists: {admin_user.username} (role: {admin_user.role})")
        else:
            print("❌ Admin user not found")
            return

        # Test login
        with app.test_client() as client:
            # Try to access download route without login
            response = client.get('/admin/download-backup/backups/afrotc695_backup_20250816_171633.json')
            print(f"Without login - Status: {response.status_code}")
            if response.status_code == 302:
                print("✅ Correctly redirected to login (expected)")
            
            # Login as admin
            login_response = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=True)
            print(f"Login response status: {login_response.status_code}")
            
            # Check if we're logged in
            if 'user_id' in session:
                print(f"✅ Logged in as user ID: {session.get('user_id')}, role: {session.get('role')}")
            else:
                print("❌ Not logged in after login attempt")
                return
            
            # Try download again
            download_response = client.get('/admin/download-backup/backups/afrotc695_backup_20250816_171633.json')
            print(f"With login - Status: {download_response.status_code}")
            print(f"Content-Type: {download_response.headers.get('Content-Type', 'None')}")
            
            if download_response.status_code == 200:
                print("✅ Download successful!")
            else:
                print(f"❌ Download failed: {download_response.data.decode()[:200]}")

if __name__ == "__main__":
    test_auth()
