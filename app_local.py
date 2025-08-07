import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import bcrypt
import json
import csv
import io
import schedule
import threading
import time
from sqlalchemy.pool import NullPool
# Neon import removed - using SQLAlchemy with psycopg2 instead
from dotenv import load_dotenv
# from vercel_blob import put, del_, list, head  # Temporarily commented out for database initialization

# Load environment variables from env.local for local development
load_dotenv('env.local')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure database for local development with Neon PostgreSQL
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///afrotc695.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure connection pooling for Neon PostgreSQL
if database_url and 'postgresql' in database_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "poolclass": NullPool,
        "connect_args": {
            "sslmode": "require"
        }
    }

# Neon serverless connection removed - using SQLAlchemy with psycopg2 instead

db = SQLAlchemy(app)

# Database Models (same as api/app.py)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    password_history = db.Column(db.Text, default='[]')  # JSON array of password hashes
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)

class Recruit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    high_school = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    sat_score = db.Column(db.Integer)
    act_score = db.Column(db.Integer)
    interests = db.Column(db.Text)
    status = db.Column(db.String(20), default='prospect')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact_method = db.Column(db.String(50))
    last_contact = db.Column(db.DateTime)
    next_follow_up = db.Column(db.DateTime)

class Cadet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    rank = db.Column(db.String(20))
    class_year = db.Column(db.Integer)
    major = db.Column(db.String(100))
    gpa = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    organization = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    event_type = db.Column(db.String(50))
    max_participants = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExternalLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Utility Functions (same as api/app.py)
def log_activity(user_id, action, details=None, ip_address=None, user_agent=None):
    """Log user activity for audit purposes"""
    try:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

def check_password_history(user, new_password):
    """Check if new password was used recently"""
    try:
        history = json.loads(user.password_history or '[]')
        new_hash = generate_password_hash(new_password)
        return new_hash in history
    except:
        return False

def update_password_history(user, new_password):
    """Update password history"""
    try:
        history = json.loads(user.password_history or '[]')
        new_hash = generate_password_hash(new_password)
        history.append(new_hash)
        # Keep only last 5 passwords
        if len(history) > 5:
            history = history[-5:]
        user.password_history = json.dumps(history)
    except Exception as e:
        print(f"Error updating password history: {e}")

# File Storage Functions (using Vercel Blob for consistency)
def upload_file_to_blob(file, folder="uploads"):
    """Upload file to Vercel Blob storage - TEMPORARILY DISABLED"""
    print("File upload temporarily disabled during database initialization")
    return None

def delete_file_from_blob(blob_url):
    """Delete file from Vercel Blob storage - TEMPORARILY DISABLED"""
    print("File deletion temporarily disabled during database initialization")
    return False

# Database backup functions (using Vercel Blob for consistency)
def backup_database(description="Manual backup"):
    """Create a database backup with timestamp and description"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}_{description.replace(' ', '_')}.json"
        
        # Export all data to JSON
        backup_data = {
            'timestamp': timestamp,
            'description': description,
            'users': [],
            'recruits': [],
            'cadets': [],
            'contacts': [],
            'events': [],
            'documents': [],
            'external_links': [],
            'activity_logs': []
        }
        
        # Export each table
        for user in User.query.all():
            backup_data['users'].append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active
            })
        
        for recruit in Recruit.query.all():
            backup_data['recruits'].append({
                'id': recruit.id,
                'first_name': recruit.first_name,
                'last_name': recruit.last_name,
                'email': recruit.email,
                'phone': recruit.phone,
                'high_school': recruit.high_school,
                'graduation_year': recruit.graduation_year,
                'gpa': recruit.gpa,
                'sat_score': recruit.sat_score,
                'act_score': recruit.act_score,
                'interests': recruit.interests,
                'status': recruit.status,
                'notes': recruit.notes,
                'created_at': recruit.created_at.isoformat() if recruit.created_at else None,
                'updated_at': recruit.updated_at.isoformat() if recruit.updated_at else None,
                'assigned_to': recruit.assigned_to,
                'contact_method': recruit.contact_method,
                'last_contact': recruit.last_contact.isoformat() if recruit.last_contact else None,
                'next_follow_up': recruit.next_follow_up.isoformat() if recruit.next_follow_up else None
            })
        
        # Add other tables similarly...
        
        # Convert to JSON string
        backup_json = json.dumps(backup_data, indent=2, default=str)
        
        # Upload to Vercel Blob - TEMPORARILY DISABLED
        print("Backup to blob temporarily disabled during database initialization")
        
        return None, backup_filename
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None, None

def get_backup_files():
    """Get list of available backup files with metadata - TEMPORARILY DISABLED"""
    print("Backup file listing temporarily disabled during database initialization")
    return []

# Routes (same as api/app.py)
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
                flash('Account is deactivated. Please contact administrator.', 'error')
                return render_template('login.html')
            
            if user.locked_until and user.locked_until > datetime.utcnow():
                flash('Account is temporarily locked. Please try again later.', 'error')
                return render_template('login.html')
            
            # Reset failed login attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            log_activity(user.id, 'login', ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent'))
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                db.session.commit()
            
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_activity(session['user_id'], 'logout', ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent'))
    
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get statistics
    total_recruits = Recruit.query.count()
    total_cadets = Cadet.query.count()
    total_contacts = Contact.query.count()
    total_events = Event.query.count()
    
    # Get recent activity
    recent_recruits = Recruit.query.order_by(Recruit.created_at.desc()).limit(5).all()
    recent_events = Event.query.order_by(Event.start_date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_recruits=total_recruits,
                         total_cadets=total_cadets,
                         total_contacts=total_contacts,
                         total_events=total_events,
                         recent_recruits=recent_recruits,
                         recent_events=recent_events)

# Add other routes as needed...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
