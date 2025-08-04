# AFROTC 695 Production Deployment Guide

## 🚀 Overview
This guide provides step-by-step instructions for deploying the AFROTC 695 Recruitment Management System on web hosting providers like Namecheap that support MySQL and Python.

## 📋 Prerequisites
- Web hosting account with Python support (Namecheap, HostGator, etc.)
- MySQL database access
- SSH access (recommended)
- Domain name (optional)

## 🗄️ Database Setup

### 1. Create MySQL Database
1. Log into your hosting control panel
2. Navigate to MySQL Databases
3. Create a new database named `afrotc695`
4. Create a database user with full privileges
5. Note down the database credentials:
   - Database name: `afrotc695`
   - Username: `your_username`
   - Password: `your_password`
   - Host: `localhost` (usually)

### 2. Database Configuration
Update the `env_production.txt` file with your actual database credentials:
```
DATABASE_URL=mysql://your_username:your_password@localhost/afrotc695
```

## 📁 File Upload

### 1. Upload Files to Server
1. Use FTP/SFTP to upload all files to your hosting directory
2. Ensure the following files are uploaded:
   - `app_production.py`
   - `wsgi.py`
   - `requirements_production.txt`
   - `env_production.txt` (rename to `.env`)
   - All files in `templates/` folder
   - All files in `static/` folder (if any)

### 2. Directory Structure
Your hosting directory should look like:
```
public_html/
├── app_production.py
├── wsgi.py
├── requirements_production.txt
├── .env
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   └── ... (all template files)
├── uploads/          (will be created automatically)
└── backups/          (will be created automatically)
```

## 🐍 Python Environment Setup

### 1. Install Dependencies
If your hosting provider supports SSH:
```bash
# Connect via SSH
ssh username@your-domain.com

# Navigate to your project directory
cd public_html

# Install Python dependencies
pip install -r requirements_production.txt
```

If SSH is not available, use your hosting provider's Python package manager in the control panel.

### 2. Required Python Packages
The system requires these packages:
- Flask
- Flask-SQLAlchemy
- PyMySQL
- cryptography
- Werkzeug
- pandas
- openpyxl
- reportlab
- python-dotenv
- schedule
- gunicorn

## ⚙️ Configuration

### 1. Environment Variables
1. Rename `env_production.txt` to `.env`
2. Update the following values:
   ```
   DATABASE_URL=mysql://your_username:your_password@localhost/afrotc695
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ```

### 2. Security Settings
- Change the `SECRET_KEY` to a strong, random string
- Ensure `FLASK_DEBUG=False` for production
- Set appropriate file upload limits

## 🌐 Web Server Configuration

### 1. Namecheap Hosting
1. Log into your Namecheap hosting control panel
2. Navigate to "Advanced" → "Python"
3. Set the Python version to 3.8 or higher
4. Set the application entry point to `wsgi.py`
5. Set the application startup file to `app_production.py`

### 2. .htaccess Configuration
Create a `.htaccess` file in your root directory:
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ /wsgi.py/$1 [QSA,L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
```

## 🔧 Database Initialization

### 1. First Run Setup
1. Access your application URL
2. The system will automatically create database tables
3. Default admin credentials:
   - Username: `admin`
   - Password: `admin123`
4. **IMPORTANT**: Change the admin password immediately after first login

### 2. Database Tables
The system will create these tables:
- `user` - User accounts and authentication
- `potential_recruit` - Potential recruit data
- `cadet` - Cadet information
- `university_contact` - High school contacts
- `recruitment_event` - Calendar events
- `activity_log` - System activity tracking
- `external_link` - Recruitment materials links
- `recruitment_document` - Document storage

## 🔒 Security Configuration

### 1. Password Security
1. Change default admin password immediately
2. Set up strong passwords for all users
3. Enable password expiration policies

### 2. File Permissions
Set appropriate file permissions:
```bash
chmod 644 .env
chmod 755 uploads/
chmod 755 backups/
chmod 644 *.py
chmod 644 templates/*
```

### 3. SSL Certificate
1. Enable SSL/HTTPS for your domain
2. Redirect all HTTP traffic to HTTPS
3. Update your `.htaccess` file to force HTTPS

## 📊 Monitoring and Maintenance

### 1. Log Monitoring
- Monitor application logs for errors
- Check database performance
- Monitor file upload usage

### 2. Backup Strategy
- Enable automated database backups
- Set up file backup for uploads
- Test restore procedures regularly

### 3. Updates
- Keep Python packages updated
- Monitor for security updates
- Test updates in staging environment first

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Error
- Verify database credentials in `.env`
- Check if MySQL service is running
- Ensure database user has proper permissions

#### 2. Import Errors
- Verify all required packages are installed
- Check Python version compatibility
- Ensure all files are uploaded correctly

#### 3. File Upload Issues
- Check file permissions on uploads directory
- Verify file size limits in configuration
- Ensure proper file type validation

#### 4. Performance Issues
- Enable database query caching
- Optimize file upload handling
- Monitor server resource usage

## 📞 Support

### Hosting Provider Support
- Contact your hosting provider for Python/MySQL setup
- Request assistance with server configuration
- Ask about SSL certificate installation

### Application Support
- Check application logs for error details
- Verify all configuration settings
- Test database connectivity

## 🔄 Migration from Local Development

### 1. Data Migration
If you have existing data in your local SQLite database:
1. Export data from local database
2. Import data to MySQL database
3. Verify data integrity after migration

### 2. Configuration Updates
1. Update database connection strings
2. Modify file paths for production
3. Update security settings

### 3. Testing
1. Test all functionality in production
2. Verify user authentication
3. Test file upload/download features
4. Check mobile responsiveness

---

**Created:** Production deployment guide  
**Last Updated:** Current system version  
**Status:** Ready for deployment 