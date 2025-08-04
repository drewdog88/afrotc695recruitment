# AFROTC 695 Recruitment Management System

This repository contains a comprehensive recruitment management system for AFROTC Detachment 695 at the University of Portland.

## Project Overview

This web application is designed to streamline and secure the recruitment process for Air Force ROTC Detachment 695. It provides tools for tracking potential recruits, managing existing cadre, coordinating with university contacts, and scheduling recruitment events.

## Features

### 1. Potential Recruit Tracking
- Track potential recruits from high schools and colleges
- Store: name, major, school, high school graduation year, expected college graduation year
- Generate reports and analytics

### 2. Cadre Management
- Manage existing AFROTC cadre information
- Track: graduation year, major, cadet rank, hometown, officer interest, enrollment status
- Record unenrollment reasons
- Form-based data entry with table display

### 3. University Contact Management
- Maintain contact list for recruitment coordination
- Calendar integration for recruitment events
- Event scheduling and tracking

### 4. Security & Administration
- Secure authentication system
- Role-based access control (Admin/User)
- Usage tracking and analytics
- Multi-administrator support

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML/CSS/JavaScript with Bootstrap 5
- **Database**: SQLite
- **Authentication**: Session-based with Werkzeug
- **Styling**: Bootstrap 5 with custom CSS
- **Templates**: Jinja2

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation

#### Option 1: Quick Start (Recommended)

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

#### Option 2: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/drewdog88/afrotc695recruitment.git
cd afrotc695recruitment
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration (optional)
```

5. Start the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

**Default Login:**
- Username: `admin`
- Password: `admin123`

## Project Structure

```
afrotc695recruitment/
├── app.py                 # Main Flask application
├── run.py                 # Application startup script
├── start.bat              # Windows startup script
├── start.sh               # macOS/Linux startup script
├── templates/             # HTML templates (Jinja2)
├── static/                # Static files (CSS, JS, images)
├── instance/              # Database and instance files
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
└── .env                  # Environment variables (created automatically)
```

## Contributing

This project is for official AFROTC use. Please follow the established guidelines for contributing to this project.

## License

This project is for official AFROTC use. 