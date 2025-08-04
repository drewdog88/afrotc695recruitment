#!/usr/bin/env python3
"""
AFROTC 695 Recruitment Management System - Production Version
Configured for MySQL database and web hosting deployment
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import pandas as pd
import uuid
import zipfile
import tempfile
import shutil
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import schedule
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Production Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://username:password@localhost/afrotc695')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='recruiter')  # admin or recruiter
    is_active = db.Column(db.Boolean, default=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    secret_question = db.Column(db.String(200), nullable=False)
    secret_answer_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PotentialRecruit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    high_school = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    interest_level = db.Column(db.String(20))  # high, medium, low
    status = db.Column(db.String(20), default='active')  # active, inactive
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Cadet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    graduation_year = db.Column(db.Integer, nullable=False)
    cadet_rank = db.Column(db.String(50))
    position = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, inactive, graduated
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UniversityContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100))
    high_school_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    relationship = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RecruitmentEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    associated_high_school = db.Column(db.String(100))
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExternalLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RecruitmentDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    category = db.Column(db.String(50), default='general')
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Helper Functions
def log_activity(user_id, action, table_name=None, record_id=None, details=None):
    """Log user activity"""
    try:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

def validate_secret_answer(user, secret_answer):
    """Validate user's secret answer"""
    return check_password_hash(user.secret_answer_hash, secret_answer.lower().strip())

def get_cadet_retention_data():
    """Calculate cadet retention data by graduation year"""
    current_year = datetime.now().year
    retention_data = []
    graduation_years = [current_year + i for i in range(4)]

    for year in graduation_years:
        total_cadets = Cadet.query.filter_by(graduation_year=year).count()
        if total_cadets > 0:
            active_cadets = Cadet.query.filter_by(graduation_year=year, status='active').count()
            active_percentage = (active_cadets / total_cadets) * 100
            inactive_percentage = 100 - active_percentage
            retention_data.append({
                'year': year,
                'total_cadets': total_cadets,
                'active_cadets': active_cadets,
                'inactive_cadets': total_cadets - active_cadets,
                'active_percentage': round(active_percentage, 1),
                'inactive_percentage': round(inactive_percentage, 1)
            })
        else:
            retention_data.append({
                'year': year, 'total_cadets': 0, 'active_cadets': 0,
                'inactive_cadets': 0, 'active_percentage': 0, 'inactive_percentage': 0
            })
    retention_data.sort(key=lambda x: x['year'])
    return retention_data

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Account is locked. Please contact administrator.', 'error')
                return render_template('login.html')
            
            # Check password expiration (180 days for non-admin users)
            if user.role != 'admin':
                days_since_change = (datetime.utcnow() - user.password_changed_at).days
                if days_since_change > 180:
                    flash('Password expired. Please change your password.', 'warning')
                    session['user_id'] = user.id
                    return redirect(url_for('change_password'))
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            log_activity(user.id, 'login')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_activity(session['user_id'], 'logout')
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get counts for dashboard
    recruit_count = PotentialRecruit.query.count()
    cadet_count = Cadet.query.filter_by(status='active').count()
    contact_count = UniversityContact.query.filter_by(is_active=True).count()
    event_count = RecruitmentEvent.query.filter_by(status='scheduled').count()
    
    # Get cadet retention data
    retention_data = get_cadet_retention_data()
    
    # Get recent activities (last 10)
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         recruit_count=recruit_count,
                         cadet_count=cadet_count,
                         contact_count=contact_count,
                         event_count=event_count,
                         retention_data=retention_data,
                         recent_activities=recent_activities)

# Add more routes here (recruits, cadets, contacts, calendar, materials, admin, etc.)
# ... (continuing with all the existing routes from the original app.py)

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                first_name='Admin',
                last_name='User',
                email='admin@afrotc695.com',
                role='admin',
                secret_question='What is your favorite color?',
                secret_answer_hash=generate_password_hash('blue')
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")
    
    app.run(debug=False, host='0.0.0.0', port=5000) 