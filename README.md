# AFROTC 695 Recruitment Management System

A comprehensive Flask-based recruitment management system for AFROTC Detachment 695 at the University of Portland.

## Project Overview

This web application streamlines and secures the recruitment process for Air Force ROTC Detachment 695. Built with Flask and Python, it provides robust tools for tracking potential recruits, managing existing cadets, coordinating with high school contacts, scheduling recruitment events, and maintaining detailed activity logs.

## Key Features

### 🔍 **Comprehensive Data Management**
- **Potential Recruit Tracking**: Complete profiles with academic and personal information
- **Cadets Management**: Status tracking (active/inactive/graduated) with unenrollment dates
- **High School Contact Management**: Extensive contact database with edit capabilities
- **Event Calendar**: Full calendar integration with recruitment event scheduling

### 📊 **Advanced Analytics & Reporting**
- **Activity Logging**: Complete audit trail of all user actions and system changes
- **Last Modified Tracking**: Automatic timestamp tracking for all records
- **Export Functionality**: Download data in Excel, PDF, and CSV formats
- **Sortable Tables**: Click-to-sort functionality on all data columns

### 🔐 **Security & Administration**
- **Session-based Authentication**: Secure login system with role-based access
- **Comprehensive User Management**: Admin and Recruiter roles with full user lifecycle management
- **Password Security**: Password history, expiry policies, and complexity requirements
- **Forgot Password System**: Secure password recovery via secret questions
- **Account Locking**: Automatic account locking for expired passwords
- **Admin Panel**: Comprehensive administrative tools and system monitoring
- **Activity Monitoring**: Detailed logs of user actions, logins, and data changes
- **IP Address Tracking**: Security monitoring with client information logging

### 🎨 **User Experience**
- **Responsive Design**: Bootstrap 5 interface optimized for all devices
- **Background Integration**: Custom detachment imagery and branding
- **Intuitive Navigation**: Clean, professional interface with easy data access
- **Real-time Updates**: Live data updates and immediate feedback

### 💾 **Data Protection & Backup**
- **Automated Backups**: Scheduled nightly database backups
- **Manual Backup/Restore**: On-demand backup creation and restoration
- **Pre-operation Backups**: Automatic backups before destructive operations
- **Data Integrity**: Comprehensive backup verification and validation

## Technology Stack

- **Backend**: Python Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap 5
- **Authentication**: Werkzeug password hashing with session management
- **Templates**: Jinja2 templating engine
- **Data Export**: Pandas, OpenPyXL, ReportLab
- **Environment**: Python-dotenv for configuration management
- **Scheduling**: Schedule library for automated tasks

## Quick Start

### 🚀 **One-Click Setup**

**Windows:**
```bash
# Double-click start.bat or run:
start.bat
```

**macOS/Linux:**
```bash
# Make executable and run:
chmod +x start.sh
./start.sh
```

### 📋 **Manual Installation**

1. **Clone the repository:**
```bash
git clone https://github.com/drewdog88/afrotc695recruitment.git
cd afrotc695recruitment
```

2. **Create virtual environment:**
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp env.example .env
# Edit .env if needed (optional)
```

5. **Start the application:**
```bash
python run.py
```

**Access the application at:** `http://localhost:5000`

**Default Login:**
- Username: `admin`
- Password: `admin123`

## User Management System

### 👥 **Role-Based Access Control**
- **Admin Role**: Full system access including user management
- **Recruiter Role**: Access to all recruitment features except admin panel
- **Password Policies**: Enforced password complexity and history requirements

### 🔑 **Password Security Features**
- **Password History**: Prevents reuse of last 5 passwords
- **Password Expiry**: Non-admin users must change passwords every 180 days
- **Admin Password**: Never expires for continuous access
- **Account Locking**: Automatic locking for expired passwords
- **Password Complexity**: Enforced strong password requirements

### 🔒 **Forgot Password System**
- **Secret Questions**: Custom security questions for each user
- **Secure Recovery**: Multi-step password reset process
- **Answer Validation**: Hashed secret answer verification
- **Temporary Access**: Secure password reset links

### 👤 **User Profile Management**
- **Personal Information**: Name, email, and phone number tracking
- **Profile Updates**: Self-service profile modification
- **Password Changes**: Secure password update functionality
- **Account Status**: Active/inactive account management

## Database Features

### 📈 **Activity Logging System**
- Complete audit trail of all user actions
- Tracks: user, action type, affected record, IP address, timestamp
- Detailed change logging for data modifications
- Export capabilities for compliance and monitoring

### 🔄 **Data Tracking**
- Automatic `last_modified` timestamps on all records
- Change history for cadet status updates
- Comprehensive event logging for system activities
- User session tracking and monitoring

### 📋 **Enhanced Data Models**
- **User Management**: Role-based access with activity tracking
- **Potential Recruits**: Complete academic and personal profiles
- **Cadets**: Status management with graduation tracking
- **High School Contacts**: Comprehensive contact information
- **Recruitment Events**: Full calendar integration
- **Activity Logs**: Complete system audit trail

## Project Structure

```
afrotc695recruitment/
├── app.py                    # Main Flask application with all routes
├── run.py                    # Application startup and initialization
├── start.bat                 # Windows one-click startup script
├── start.sh                  # macOS/Linux one-click startup script
├── requirements.txt          # Python dependencies
├── env.example              # Environment configuration template
├── .env                     # Environment variables (auto-created)
├── templates/               # Jinja2 HTML templates
│   ├── base.html           # Base template with navigation
│   ├── dashboard.html      # Main dashboard view
│   ├── recruits.html       # Potential recruits management
│   ├── cadet.html          # Cadets management interface
│   ├── contacts.html       # High school contacts management
│   ├── calendar.html       # Event calendar view
│   ├── admin.html          # Administrative panel
│   ├── activity_log.html   # Activity logging interface
│   ├── login.html          # Login and forgot password interface
│   ├── forgot_password.html # Password recovery form
│   ├── reset_password_question.html # Secret question verification
│   ├── reset_password.html # Password reset form
│   ├── add_user.html       # User creation interface
│   ├── edit_user.html      # User profile management
│   └── [other templates]   # Additional form and view templates
├── static/                  # Static assets
│   ├── detachment695.jpg   # Background imagery
│   └── [CSS/JS files]      # Additional static resources
└── instance/               # Database and instance files
    └── afrotc695.db        # SQLite database
```

## Key Functionality

### 📊 **Data Management**
- **CRUD Operations**: Create, read, update, delete for all data types
- **Bulk Operations**: Export data in multiple formats
- **Data Validation**: Input validation and error handling
- **Search & Filter**: Advanced data filtering capabilities

### 📅 **Calendar & Events**
- **Event Scheduling**: Full recruitment event management
- **Calendar View**: Monthly calendar with event indicators
- **Event Details**: Comprehensive event information tracking
- **Integration**: Seamless integration with contact management

### 🔍 **Activity Monitoring**
- **User Actions**: Track all user interactions and data changes
- **System Events**: Monitor login/logout and system activities
- **Change History**: Detailed records of data modifications
- **Security Logs**: IP address and user agent tracking

### 📈 **Reporting & Analytics**
- **Data Export**: Excel, PDF, and CSV export capabilities
- **Activity Reports**: Comprehensive activity logging reports
- **Usage Analytics**: System usage and user activity metrics
- **Compliance**: Audit trail for regulatory compliance

### 💾 **Backup & Recovery**
- **Automated Backups**: Scheduled nightly database backups
- **Manual Backups**: On-demand backup creation
- **Restore Functionality**: Complete database restoration from backups
- **Backup Verification**: Integrity checks and validation

## Security Features

- **Password Hashing**: Secure password storage with Werkzeug
- **Session Management**: Secure session handling and timeout
- **Role-based Access**: Admin and Recruiter role permissions
- **Input Validation**: Comprehensive input sanitization
- **Activity Logging**: Complete audit trail for security monitoring
- **Password Policies**: Enforced complexity and history requirements
- **Account Security**: Automatic locking and expiry management
- **Secret Questions**: Secure password recovery system

## Contributing

This project is for official AFROTC use. Please follow established guidelines for contributing to this project.

## Support

For technical support or questions about the AFROTC 695 Recruitment Management System, please contact the system administrator.

## License

This project is for official AFROTC use. 