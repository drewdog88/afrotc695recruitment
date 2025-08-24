# AFROTC 695 Recruitment Management System

A modern, cloud-based recruitment management system for AFROTC Detachment 695 at the University of Portland. Built with Flask, deployed on Vercel, and powered by Neon PostgreSQL.

## 🚀 Overview

Streamlines recruitment operations for Air Force ROTC Detachment 695 with comprehensive data management, secure authentication, automated backups, and real-time analytics.

## ✨ Key Features

### 📊 **Data Management**
- **Recruit Tracking**: Complete profiles with academic and personal information
- **Cadet Management**: Status tracking (active/inactive/graduated) with unenrollment dates
- **Contact Management**: High school and university contact database
- **Event Calendar**: Recruitment event scheduling and management
- **Document Storage**: Secure file management with Vercel Blob storage

### 🔐 **Security & Authentication**
- **Session-based Authentication**: Secure login with role-based access (Admin/Recruiter)
- **Password Security**: Hashing, history tracking, and complexity requirements
- **Account Management**: Password recovery, account locking, user lifecycle
- **Activity Logging**: Comprehensive audit trails of all user actions

### 📈 **Analytics & Reporting**
- **System Dashboard**: Real-time metrics, database statistics, performance monitoring
- **Data Export**: Excel, PDF, and CSV export capabilities
- **Interactive Charts**: Visual data representation with Chart.js
- **Activity Monitoring**: User engagement and system usage analytics

### 💾 **Data Protection**
- **Automated Backups**: Scheduled nightly backups to Cloudflare R2 storage
- **Manual Backup/Restore**: On-demand backup creation and restoration
- **30-Day Retention**: Automatic cleanup of old backups
- **Data Integrity**: Comprehensive backup verification

## 🏗️ Architecture

### **Tech Stack**
- **Backend**: Python Flask 3.1.1 with SQLAlchemy ORM
- **Database**: Neon PostgreSQL (serverless, auto-scaling)
- **Deployment**: Vercel (serverless functions)
- **Storage**: Vercel Blob (documents) + Cloudflare R2 (backups)
- **Frontend**: Bootstrap 5, Chart.js, Jinja2 templates
- **Authentication**: Werkzeug password hashing with session management

### **Database Models**
- **User**: Authentication and user management
- **PotentialRecruit**: Prospective student tracking
- **Cadet**: Current cadet management with unenrollment tracking
- **UniversityContact**: High school and university contacts
- **RecruitmentEvent**: Event scheduling and management
- **ExternalLink**: Materials and resource links
- **RecruitmentDocument**: Document management
- **ActivityLog**: System audit trails

## 🚀 Quick Start

### **Local Development**

1. **Clone and setup:**
```bash
git clone https://github.com/drewdog88/afrotc695recruitment.git
cd afrotc695recruitment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

2. **Environment setup:**
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Neon PostgreSQL and Vercel Blob credentials
```

3. **Database initialization:**
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

4. **Run locally:**
```bash
python app_local.py
# Available at http://localhost:5000
```

### **Production Deployment**

Automatically deployed to Vercel when pushing to `master` branch.

**Production URL**: https://afrotc695recruitment.vercel.app

## 🔧 Configuration

### **Required Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Vercel Blob Storage (documents)
BLOB_READ_WRITE_TOKEN=your_vercel_blob_token

# Cloudflare R2 Storage (backups)
CLOUDFLARE_R2_ACCESS_KEY_ID=your_r2_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_r2_secret_key
CLOUDFLARE_R2_BUCKET_NAME=your_r2_bucket

# Flask
SECRET_KEY=your_secret_key
FLASK_ENV=production
```

### **Backup Configuration**
- **Daily Backups**: 7:00 PM UTC (via Vercel Cron)
- **Weekly Full Backups**: Sundays 3:00 AM UTC
- **Cleanup**: Daily 4:00 AM UTC (30-day retention)

## 📁 Project Structure

```
afrotc695recruitment/
├── app.py                 # Main Flask application
├── api/app.py            # Vercel serverless entry point
├── templates/            # Jinja2 HTML templates
├── static/              # CSS, JS, images
├── utils/               # Utility functions
├── migrations/          # Database migrations
├── tests/              # Test suite
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel deployment config
└── neon_backup_scheduler.py  # Automated backup system
```

## 🛠️ Development

### **Key Dependencies**
- **Flask 3.1.1**: Web framework
- **Flask-SQLAlchemy 3.1.1**: Database ORM
- **Werkzeug 3.1.3**: Security and utilities
- **vercel-blob 0.4.2**: Cloud file storage
- **boto3**: Cloudflare R2 backup storage
- **xlsxwriter**: Lightweight Excel export
- **fpdf2**: Lightweight PDF export

### **Testing**
```bash
# Run test suite
python -m pytest tests/

# Run specific test categories
python test_api_smoke.py
python test_blob_operations.py
python test_auth.py
```

## 🔒 Security Features

- **Authentication**: Secure session-based login system
- **Authorization**: Role-based access control (Admin/Recruiter)
- **Password Security**: Hashing, history, expiry policies
- **Activity Logging**: Comprehensive audit trails
- **Data Protection**: Encrypted backups and secure storage
- **Input Validation**: Comprehensive data validation and sanitization

## 📊 System Features

### **Recruitment Management**
- Track potential recruits with comprehensive profiles
- Manage cadet status and progression
- Coordinate with high school and university contacts
- Schedule and track recruitment events
- Export data in multiple formats

### **Administrative Tools**
- User management with role-based access
- System statistics and performance monitoring
- Activity logging and audit trails
- Database backup and restore functionality
- Document and link management

## 🚀 Deployment

### **Vercel Features**
- Serverless functions with automatic scaling
- Edge caching for improved performance
- Automatic HTTPS and CDN distribution
- Environment variable management
- Cron job scheduling for automated backups

### **Database Management**
- **Neon PostgreSQL**: Serverless, auto-scaling database
- **Connection Pooling**: Optimized database connections
- **Automatic Backups**: Nightly backups with 30-day retention
- **Data Migration**: Seamless schema updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software for AFROTC Detachment 695.

## 🆘 Support

For technical support or questions, please contact the development team.

---

**AFROTC Detachment 695** - University of Portland
*Empowering the next generation of Air Force leaders*
