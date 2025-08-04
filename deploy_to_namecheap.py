#!/usr/bin/env python3
"""
AFROTC 695 Recruitment System - Namecheap Deployment Script
This script helps prepare your Flask application for Namecheap shared hosting.
"""

import os
import zipfile
import shutil
from pathlib import Path

def create_deployment_package():
    """Create a deployment-ready ZIP package for Namecheap hosting."""
    
    print("🚀 AFROTC 695 - Creating Namecheap Deployment Package")
    print("=" * 60)
    
    # Files and directories to include
    include_files = [
        'app_production.py',
        'passenger_wsgi.py', 
        'requirements_production.txt',
        'templates/',
        'static/',
        'instance/',
        '.env.production'  # If it exists
    ]
    
    # Files and directories to exclude
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.venv',
        'venv',
        'node_modules',
        '.pytest_cache',
        '*.pyc',
        '.DS_Store',
        'Thumbs.db',
        'app.py',  # Local development file
        'requirements.txt',  # Local development requirements
        '*.log',
        'downloads/',
        'process_current_backgrounds.py',
        'optimize_any_images.py'
    ]
    
    # Create deployment directory
    deploy_dir = Path('namecheap_deployment')
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    print(f"📁 Created deployment directory: {deploy_dir}")
    
    # Copy files
    copied_files = []
    for item in include_files:
        item_path = Path(item)
        if item_path.exists():
            if item_path.is_file():
                dest = deploy_dir / item_path.name
                shutil.copy2(item_path, dest)
                copied_files.append(item)
                print(f"✅ Copied file: {item}")
            elif item_path.is_dir():
                dest = deploy_dir / item_path.name
                shutil.copytree(item_path, dest, ignore=shutil.ignore_patterns(*exclude_patterns))
                copied_files.append(item)
                print(f"✅ Copied directory: {item}")
        else:
            print(f"⚠️  Not found: {item}")
    
    # Create ZIP file
    zip_path = 'afrotc695_namecheap_deployment.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if not any(pattern in file for pattern in exclude_patterns):
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(deploy_dir)
                    zipf.write(file_path, arc_path)
    
    # Clean up temp directory
    shutil.rmtree(deploy_dir)
    
    zip_size = os.path.getsize(zip_path) / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT PACKAGE CREATED SUCCESSFULLY!")
    print(f"📦 File: {zip_path}")
    print(f"📊 Size: {zip_size:.2f} MB")
    print(f"📋 Files included: {len(copied_files)}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Log into your Namecheap cPanel")
    print("2. Go to 'Setup Python App' and create a new application")
    print("3. Upload this ZIP file to your app directory")
    print("4. Extract the files in cPanel File Manager")
    print("5. Install requirements and configure database")
    
    return zip_path

def create_env_template():
    """Create a template .env file for production."""
    
    env_content = """# AFROTC 695 Production Environment Variables
# Copy this to .env.production and update with your actual values

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this

# Database Configuration (MySQL on Namecheap)
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=your_db_username  
DB_PASSWORD=your_db_password
DB_PORT=3306

# Admin Configuration
ADMIN_EMAIL=your-email@example.com
ADMIN_PASSWORD=secure-admin-password

# Security Settings
SESSION_PERMANENT=False
PERMANENT_SESSION_LIFETIME=3600

# File Upload Settings
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
"""
    
    with open('.env.production.template', 'w') as f:
        f.write(env_content)
    
    print("📝 Created .env.production.template")
    print("   Copy this to .env.production and update with your values")

def main():
    """Main deployment preparation function."""
    print("🇺🇸 AFROTC Detachment 695 - Namecheap Deployment Tool")
    print("🎖️  Air Force ROTC Recruitment Management System")
    print()
    
    # Create environment template
    create_env_template()
    print()
    
    # Create deployment package
    zip_file = create_deployment_package()
    
    print("\n" + "🛡️ " * 30)
    print("IMPORTANT SECURITY REMINDERS:")
    print("• Change all default passwords")
    print("• Use strong, unique database credentials")
    print("• Enable SSL certificate in cPanel")
    print("• Regularly backup your database")
    print("• Keep your application updated")
    print("🛡️ " * 30)

if __name__ == "__main__":
    main()