# AFROTC 695 Production Deployment Guide

## Quick Setup for Web Hosting (Namecheap, etc.)

### 1. Database Setup
- Create MySQL database named `afrotc695`
- Create database user with full privileges
- Note credentials for configuration

### 2. File Upload
Upload these files to your hosting directory:
- `app_production.py` (main application)
- `wsgi.py` (web server entry point)
- `requirements_production.txt` (Python dependencies)
- `templates/` folder (all HTML templates)
- `env_production.txt` (rename to `.env`)

### 3. Configuration
Edit `.env` file with your database credentials:
```
DATABASE_URL=mysql://username:password@localhost/afrotc695
SECRET_KEY=your-secret-key-here
```

### 4. Python Setup
Install required packages:
```bash
pip install -r requirements_production.txt
```

### 5. Web Server
- Set Python version to 3.8+
- Set entry point to `wsgi.py`
- Enable SSL/HTTPS

### 6. First Access
- Visit your domain
- Login with: admin / admin123
- Change password immediately

## Files Included
- `app_production.py` - Production Flask app with MySQL
- `wsgi.py` - WSGI entry point
- `requirements_production.txt` - Python dependencies
- `env_production.txt` - Environment template
- `DEPLOYMENT.md` - This guide

## Support
Contact your hosting provider for Python/MySQL setup assistance. 