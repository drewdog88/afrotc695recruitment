# 🇺🇸 AFROTC 695 Namecheap Deployment Guide

## 🎖️ Air Force ROTC Recruitment Management System - Going Live!

This guide will walk you through deploying your Flask application to Namecheap shared hosting step by step.

---

## 📋 **Prerequisites**

Before starting, ensure you have:
- ✅ Namecheap shared hosting account with cPanel access
- ✅ Domain connected to your hosting 
- ✅ Your Flask application working locally
- ✅ SSH/Terminal access enabled (if available)

---

## 🚀 **Phase 1: Prepare Your Application**

### Step 1: Create Deployment Package

Run the deployment script to create a ready-to-upload package:

```bash
python deploy_to_namecheap.py
```

This creates `afrotc695_namecheap_deployment.zip` with all necessary files.

### Step 2: Prepare Environment Variables

1. Copy `.env.production.template` to `.env.production`
2. Update with your actual values:
   - Database credentials (you'll get these from cPanel)
   - Secret key (generate a secure one)
   - Admin email and password

---

## 🌐 **Phase 2: Namecheap cPanel Setup**

### Step 1: Access Your cPanel

1. Log into your Namecheap account
2. Go to "Hosting List" 
3. Click "GO TO CPANEL" for your domain

### Step 2: Create MySQL Database

1. In cPanel, find **"MySQL Databases"**
2. Create a new database:
   - Database name: `afrotc695_db` (or similar)
3. Create a database user:
   - Username: `afrotc695_user` (or similar)  
   - Password: (generate strong password)
4. Add user to database with **ALL PRIVILEGES**
5. **Save these credentials** - you'll need them!

### Step 3: Set Up Python Application

1. In cPanel, find **"Setup Python App"** (under Software)
2. Click **"+ CREATE APPLICATION"**
3. Configure:
   - **Python version**: Select newest available (3.9+ recommended)
   - **Application root**: `afrotc695` (or your preferred name)
   - **Application URL**: Select your domain, leave path empty
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`
4. Click **"CREATE"**

### Step 4: Upload Your Files

#### Method A: File Manager (Easiest)
1. Go to **"File Manager"** in cPanel
2. Navigate to your app directory (created above)
3. Click **"Upload"**
4. Upload `afrotc695_namecheap_deployment.zip`
5. Right-click the ZIP file → **"Extract"**
6. Move all extracted files to the app root directory
7. Delete the empty ZIP file

#### Method B: FTP (Alternative)
1. Use FileZilla or similar FTP client
2. Connect to your hosting
3. Upload files to your app directory

---

## ⚙️ **Phase 3: Configure Application**

### Step 1: Install Python Dependencies

1. In cPanel, go back to **"Setup Python App"**
2. Find your application and click **"Edit"**
3. Copy the virtual environment command shown
4. Go to **"Terminal"** in cPanel (under Advanced)
5. Paste and run the virtual environment command
6. Install requirements:
   ```bash
   pip install -r requirements_production.txt
   ```

### Step 2: Configure Environment Variables

In the Python App settings, add these environment variables:

| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `DB_HOST` | `localhost` |
| `DB_NAME` | `your_database_name` |
| `DB_USER` | `your_db_username` |
| `DB_PASSWORD` | `your_db_password` |
| `SECRET_KEY` | `your-generated-secret-key` |

### Step 3: Initialize Database

1. In Terminal, activate your virtual environment
2. Run database setup:
   ```bash
   python -c "from app_production import db; db.create_all()"
   ```

### Step 4: Create Admin User

```bash
python -c "
from app_production import app, db, User
from werkzeug.security import generate_password_hash
with app.app_context():
    admin = User(
        username='admin',
        email='your-email@example.com',
        password=generate_password_hash('your-secure-password'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')
"
```

---

## 🔒 **Phase 4: Security & SSL**

### Step 1: Enable SSL Certificate

1. In cPanel, go to **"SSL/TLS"**
2. Use **"Let's Encrypt"** (free) or upload your own
3. Force HTTPS redirects in **"Force HTTPS Redirect"**

### Step 2: Configure Security Headers

Create/edit `.htaccess` in your app directory:

```apache
# AFROTC 695 Security Headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options SAMEORIGIN
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# Flask App Routing
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,L]
```

---

## 🎯 **Phase 5: Final Testing**

### Step 1: Start Your Application

1. In cPanel Python App settings
2. Click **"RESTART"** or **"START APP"**
3. Wait for the green "Running" status

### Step 2: Test Your Website

1. Visit your domain: `https://yourdomain.com`
2. Test login functionality
3. Test all major features:
   - Dashboard access
   - User management
   - Database operations
   - File uploads
   - Air Force backgrounds

### Step 3: Monitor Performance

- Check **error logs** in cPanel if issues arise
- Monitor database performance
- Test from different devices/browsers

---

## 🛠️ **Troubleshooting Common Issues**

### Application Won't Start
- Check error logs in cPanel
- Verify all required files uploaded
- Ensure `passenger_wsgi.py` is correct
- Check Python version compatibility

### Database Connection Errors
- Verify database credentials in environment variables
- Ensure database user has proper privileges
- Check MySQL service status

### Missing Static Files (CSS/JS/Images)
- Ensure `static/` folder uploaded completely
- Check file permissions
- Verify Air Force background images are present

### Python Module Errors
- Re-run `pip install -r requirements_production.txt`
- Check Python version compatibility
- Some modules might need binary installation

---

## 📞 **Support Resources**

- **Namecheap Support**: Live chat or ticket system
- **cPanel Documentation**: Extensive help within cPanel
- **Python App Logs**: Available in cPanel for debugging

---

## 🎖️ **Deployment Checklist**

- [ ] Created MySQL database and user
- [ ] Uploaded application files
- [ ] Configured Python app in cPanel
- [ ] Installed requirements
- [ ] Set environment variables
- [ ] Initialized database
- [ ] Created admin user
- [ ] Enabled SSL certificate
- [ ] Tested all functionality
- [ ] Configured security headers
- [ ] Verified Air Force backgrounds loading
- [ ] Tested from multiple browsers

---

## 🇺🇸 **Ready for Service!**

Once all steps are complete, your AFROTC 695 Recruitment Management System will be live and ready to help recruit the next generation of Air Force officers!

**Honor Guard. Develop. Respect.**