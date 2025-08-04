from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timezone
import os
import shutil
import sqlite3
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile
import zipfile

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
# Use absolute path for database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'afrotc695.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database backup configuration
BACKUP_DIR = 'backups'
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def backup_database(description="Manual backup"):
    """Create a database backup with timestamp and description"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"afrotc695_backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Get the current database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not db_path.startswith('/'):
            db_path = os.path.join(os.getcwd(), db_path)
        
        # Create backup
        shutil.copy2(db_path, backup_path)
        
        # Create backup metadata
        metadata = {
            'timestamp': timestamp,
            'description': description,
            'filename': backup_filename,
            'size': os.path.getsize(backup_path),
            'user': session.get('username', 'Unknown')
        }
        
        # Save metadata to a JSON file
        import json
        metadata_file = backup_path.replace('.db', '_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Database backup created: {backup_filename}")
        return backup_filename, backup_path
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None, None

def restore_database(backup_file_path):
    """Restore database from backup file"""
    try:
        # Get the current database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not db_path.startswith('/'):
            db_path = os.path.join(os.getcwd(), db_path)
        
        # Create a backup of current database before restore
        current_backup = backup_database("Pre-restore backup")
        
        # Close database connections
        db.session.close()
        
        # Restore from backup
        shutil.copy2(backup_file_path, db_path)
        
        print(f"Database restored from: {backup_file_path}")
        return True
        
    except Exception as e:
        print(f"Error restoring database: {e}")
        return False

def get_backup_files():
    """Get list of available backup files with metadata"""
    backups = []
    try:
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.db'):
                backup_path = os.path.join(BACKUP_DIR, filename)
                metadata_file = backup_path.replace('.db', '_metadata.json')
                
                # Get basic file info
                file_stat = os.stat(backup_path)
                backup_info = {
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created': datetime.fromtimestamp(file_stat.st_ctime),
                    'description': 'Manual backup'
                }
                
                # Try to load metadata
                if os.path.exists(metadata_file):
                    try:
                        import json
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            backup_info.update(metadata)
                    except:
                        pass
                
                backups.append(backup_info)
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
        
    except Exception as e:
        print(f"Error getting backup files: {e}")
        return []

# Activity Log Model for tracking all user actions
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)  # Store username for easy reference
    action = db.Column(db.String(100), nullable=False)  # e.g., 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT'
    table_name = db.Column(db.String(50))  # e.g., 'user', 'potential_recruit', 'cadre', etc.
    record_id = db.Column(db.Integer)  # ID of the affected record
    record_description = db.Column(db.String(200))  # Human-readable description of the record
    details = db.Column(db.Text)  # Additional details about the action
    ip_address = db.Column(db.String(45))  # Store IP address for security
    user_agent = db.Column(db.String(500))  # Store user agent for security
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = db.relationship('User', backref='activity_logs')

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PotentialRecruit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    major = db.Column(db.String(100))
    current_school = db.Column(db.String(100), nullable=False)
    school_type = db.Column(db.String(20), nullable=False)  # high_school or college
    high_school_graduation_year = db.Column(db.Integer)
    expected_college_graduation_year = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    sat_score = db.Column(db.Integer)
    act_score = db.Column(db.Integer)
    interests = db.Column(db.Text)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='prospective')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Cadre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    major = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    cadet_rank = db.Column(db.String(50), nullable=False)
    hometown = db.Column(db.String(100))
    officer_interest = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, inactive, graduated
    unenrollment_reason = db.Column(db.Text)
    unenrollment_date = db.Column(db.Date)
    gpa = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        # Handle unenrollment_date parsing
        if 'unenrollment_date' in kwargs and kwargs['unenrollment_date']:
            try:
                if isinstance(kwargs['unenrollment_date'], str):
                    kwargs['unenrollment_date'] = datetime.strptime(kwargs['unenrollment_date'], '%Y-%m-%d').date()
                elif hasattr(kwargs['unenrollment_date'], 'date'):
                    # If it's already a date object
                    kwargs['unenrollment_date'] = kwargs['unenrollment_date'].date()
                else:
                    kwargs['unenrollment_date'] = None
            except (ValueError, TypeError, AttributeError):
                kwargs['unenrollment_date'] = None
        super().__init__(**kwargs)
    
    @property
    def unenrollment_date_display(self):
        """Safe property to get unenrollment_date for display"""
        try:
            if self.unenrollment_date:
                if hasattr(self.unenrollment_date, 'strftime'):
                    return self.unenrollment_date.strftime('%Y-%m-%d')
                elif isinstance(self.unenrollment_date, str):
                    # Try to parse and format
                    parsed_date = datetime.strptime(self.unenrollment_date, '%Y-%m-%d')
                    return parsed_date.strftime('%Y-%m-%d')
                else:
                    return None
            return None
        except (ValueError, TypeError, AttributeError):
            return None

class UniversityContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    university_name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_title = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RecruitmentEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(200))
    university_id = db.Column(db.Integer, db.ForeignKey('university_contact.id'))
    event_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    attendees_count = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt is None:
        return None
    # Convert UTC to local time (this will use the server's timezone)
    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone()
    return local_dt

# Helper function to log activities
def log_activity(action, table_name=None, record_id=None, record_description=None, details=None):
    """Log user activity to the database"""
    if 'user_id' not in session:
        return
    
    try:
        # Get user info
        user_id = session['user_id']
        username = session.get('username', 'Unknown')
        
        # Get request info
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Create activity log entry
        activity = ActivityLog(
            user_id=user_id,
            username=username,
            action=action,
            table_name=table_name,
            record_id=record_id,
            record_description=record_description,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        # Don't fail the main operation if logging fails
        db.session.rollback()

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
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            # Log successful login
            log_activity('LOGIN', details=f'User {username} logged in successfully')
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Log failed login attempt
            log_activity('LOGIN_FAILED', details=f'Failed login attempt for username: {username}')
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        username = session.get('username', 'Unknown')
        log_activity('LOGOUT', details=f'User {username} logged out')
    
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get counts for dashboard
    recruit_count = PotentialRecruit.query.count()
    cadre_count = Cadre.query.filter_by(status='active').count()
    contact_count = UniversityContact.query.filter_by(is_active=True).count()
    event_count = RecruitmentEvent.query.filter_by(status='scheduled').count()
    
    return render_template('dashboard.html', 
                         recruit_count=recruit_count,
                         cadre_count=cadre_count,
                         contact_count=contact_count,
                         event_count=event_count)

@app.route('/recruits')
def recruits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get sort parameters
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Define valid sort columns
    valid_sorts = {
        'first_name': PotentialRecruit.first_name,
        'last_name': PotentialRecruit.last_name,
        'email': PotentialRecruit.email,
        'current_school': PotentialRecruit.current_school,
        'major': PotentialRecruit.major,
        'status': PotentialRecruit.status,
        'created_at': PotentialRecruit.created_at,
        'last_modified': PotentialRecruit.last_modified
    }
    
    # Default to created_at if invalid sort column
    if sort_by not in valid_sorts:
        sort_by = 'created_at'
    
    # Apply sorting
    if order == 'asc':
        recruits = PotentialRecruit.query.order_by(valid_sorts[sort_by].asc()).all()
    else:
        recruits = PotentialRecruit.query.order_by(valid_sorts[sort_by].desc()).all()
    
    return render_template('recruits.html', recruits=recruits, sort_by=sort_by, order=order)

@app.route('/recruits/add', methods=['GET', 'POST'])
def add_recruit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Create backup before adding new recruit
        backup_database("Pre-add recruit backup")
        
        recruit = PotentialRecruit(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            major=request.form['major'],
            current_school=request.form['current_school'],
            school_type=request.form['school_type'],
            high_school_graduation_year=request.form.get('high_school_graduation_year'),
            expected_college_graduation_year=request.form.get('expected_college_graduation_year'),
            gpa=request.form.get('gpa'),
            sat_score=request.form.get('sat_score'),
            act_score=request.form.get('act_score'),
            interests=request.form['interests'],
            notes=request.form['notes'],
            status=request.form['status']
        )
        
        db.session.add(recruit)
        db.session.commit()
        
        # Log the activity
        log_activity(
            'CREATE',
            'potential_recruit',
            recruit.id,
            f"Recruit: {recruit.first_name} {recruit.last_name}",
            f"Added new recruit from {recruit.current_school}"
        )
        
        flash('Recruit added successfully!', 'success')
        return redirect(url_for('recruits'))
    
    return render_template('add_recruit.html')

@app.route('/cadre')
def cadre():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get sort parameters
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Define valid sort columns
    valid_sorts = {
        'first_name': Cadre.first_name,
        'last_name': Cadre.last_name,
        'email': Cadre.email,
        'cadet_rank': Cadre.cadet_rank,
        'major': Cadre.major,
        'graduation_year': Cadre.graduation_year,
        'status': Cadre.status,
        'gpa': Cadre.gpa,
        'created_at': Cadre.created_at,
        'last_modified': Cadre.last_modified
    }
    
    # Default to created_at if invalid sort column
    if sort_by not in valid_sorts:
        sort_by = 'created_at'
    
    # Apply sorting
    if order == 'asc':
        cadre_members = Cadre.query.order_by(valid_sorts[sort_by].asc()).all()
    else:
        cadre_members = Cadre.query.order_by(valid_sorts[sort_by].desc()).all()
    
    return render_template('cadre.html', cadre_members=cadre_members, sort_by=sort_by, order=order)

@app.route('/cadre/add', methods=['GET', 'POST'])
def add_cadre():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Create backup before adding new cadre
        backup_database("Pre-add cadre backup")
        
        # Handle unenrollment_date parsing
        unenrollment_date = None
        if request.form.get('unenrollment_date'):
            try:
                unenrollment_date = datetime.strptime(request.form['unenrollment_date'], '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid unenrollment date format. Please use YYYY-MM-DD.', 'error')
                return render_template('add_cadre.html')
        
        cadre = Cadre(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            major=request.form['major'],
            graduation_year=request.form['graduation_year'],
            cadet_rank=request.form['cadet_rank'],
            hometown=request.form['hometown'],
            officer_interest=request.form['officer_interest'],
            status=request.form['status'],
            unenrollment_reason=request.form['unenrollment_reason'],
            unenrollment_date=unenrollment_date,
            gpa=request.form.get('gpa')
        )
        
        db.session.add(cadre)
        db.session.commit()
        
        # Log the activity
        log_activity(
            'CREATE',
            'cadre',
            cadre.id,
            f"Cadre: {cadre.first_name} {cadre.last_name} ({cadre.cadet_rank})",
            f"Added new cadre member with status: {cadre.status}"
        )
        
        flash('Cadre member added successfully!', 'success')
        return redirect(url_for('cadre'))
    
    return render_template('add_cadre.html')

@app.route('/cadre/edit/<int:cadre_id>', methods=['GET', 'POST'])
def edit_cadre(cadre_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cadre = Cadre.query.get_or_404(cadre_id)
    
    if request.method == 'POST':
        # Store old values for logging
        old_status = cadre.status
        old_rank = cadre.cadet_rank
        
        cadre.first_name = request.form['first_name']
        cadre.last_name = request.form['last_name']
        cadre.email = request.form['email']
        cadre.phone = request.form['phone']
        cadre.major = request.form['major']
        cadre.graduation_year = request.form['graduation_year']
        cadre.cadet_rank = request.form['cadet_rank']
        cadre.hometown = request.form['hometown']
        cadre.officer_interest = request.form['officer_interest']
        cadre.status = request.form['status']
        cadre.unenrollment_reason = request.form['unenrollment_reason']
        cadre.gpa = request.form.get('gpa')
        
        # Handle unenrollment_date parsing
        if request.form.get('unenrollment_date'):
            try:
                cadre.unenrollment_date = datetime.strptime(request.form['unenrollment_date'], '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid unenrollment date format. Please use YYYY-MM-DD.', 'error')
                return render_template('edit_cadre.html', cadre=cadre)
        else:
            cadre.unenrollment_date = None
        
        db.session.commit()
        
        # Log the activity
        changes = []
        if old_status != cadre.status:
            changes.append(f"Status: {old_status} → {cadre.status}")
        if old_rank != cadre.cadet_rank:
            changes.append(f"Rank: {old_rank} → {cadre.cadet_rank}")
        
        log_activity(
            'UPDATE',
            'cadre',
            cadre.id,
            f"Cadre: {cadre.first_name} {cadre.last_name}",
            f"Updated cadre member. Changes: {', '.join(changes) if changes else 'General update'}"
        )
        
        flash('Cadre member updated successfully!', 'success')
        return redirect(url_for('cadre'))
    
    return render_template('edit_cadre.html', cadre=cadre)

@app.route('/contacts')
def contacts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get sort parameters
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Define valid sort columns
    valid_sorts = {
        'university_name': UniversityContact.university_name,
        'contact_name': UniversityContact.contact_name,
        'contact_title': UniversityContact.contact_title,
        'email': UniversityContact.email,
        'phone': UniversityContact.phone,
        'is_active': UniversityContact.is_active,
        'created_at': UniversityContact.created_at,
        'last_modified': UniversityContact.last_modified
    }
    
    # Default to created_at if invalid sort column
    if sort_by not in valid_sorts:
        sort_by = 'created_at'
    
    # Apply sorting
    if order == 'asc':
        contacts = UniversityContact.query.order_by(valid_sorts[sort_by].asc()).all()
    else:
        contacts = UniversityContact.query.order_by(valid_sorts[sort_by].desc()).all()
    
    return render_template('contacts.html', contacts=contacts, sort_by=sort_by, order=order)

@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Create backup before adding new contact
        backup_database("Pre-add contact backup")
        
        contact = UniversityContact(
            university_name=request.form['university_name'],
            contact_name=request.form['contact_name'],
            contact_title=request.form['contact_title'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            notes=request.form['notes']
        )
        
        db.session.add(contact)
        db.session.commit()
        
        # Log the activity
        log_activity(
            'CREATE',
            'university_contact',
            contact.id,
            f"Contact: {contact.contact_name} at {contact.university_name}",
            f"Added new university contact"
        )
        
        flash('Contact added successfully!', 'success')
        return redirect(url_for('contacts'))
    
    return render_template('add_contact.html')

@app.route('/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    contact = UniversityContact.query.get_or_404(contact_id)
    
    if request.method == 'POST':
        # Store old values for logging
        old_active = contact.is_active
        
        contact.university_name = request.form['university_name']
        contact.contact_name = request.form['contact_name']
        contact.contact_title = request.form['contact_title']
        contact.email = request.form['email']
        contact.phone = request.form['phone']
        contact.address = request.form['address']
        contact.notes = request.form['notes']
        contact.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        
        # Log the activity
        changes = []
        if old_active != contact.is_active:
            changes.append(f"Status: {'Active' if old_active else 'Inactive'} → {'Active' if contact.is_active else 'Inactive'}")
        
        log_activity(
            'UPDATE',
            'university_contact',
            contact.id,
            f"Contact: {contact.contact_name} at {contact.university_name}",
            f"Updated contact. Changes: {', '.join(changes) if changes else 'General update'}"
        )
        
        flash('Contact updated successfully!', 'success')
        return redirect(url_for('contacts'))
    
    return render_template('edit_contact.html', contact=contact)

@app.route('/calendar')
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        events = RecruitmentEvent.query.order_by(RecruitmentEvent.event_date).all()
        contacts = UniversityContact.query.filter_by(is_active=True).all()
        return render_template('calendar.html', events=events, contacts=contacts)
    except Exception as e:
        print(f"Error loading calendar: {e}")
        flash('Error loading calendar data. Please try again.', 'error')
        return render_template('calendar.html', events=[], contacts=[])

@app.route('/calendar/add', methods=['GET', 'POST'])
def add_event():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Create backup before adding new event
            backup_database("Pre-add event backup")
            
            event = RecruitmentEvent(
                title=request.form['title'],
                description=request.form['description'],
                event_date=datetime.strptime(request.form['event_date'], '%Y-%m-%d').date(),
                start_time=datetime.strptime(request.form['start_time'], '%H:%M').time() if request.form['start_time'] else None,
                end_time=datetime.strptime(request.form['end_time'], '%H:%M').time() if request.form['end_time'] else None,
                location=request.form['location'],
                university_id=request.form.get('university_id'),
                event_type=request.form['event_type'],
                notes=request.form['notes']
            )
            
            db.session.add(event)
            db.session.commit()
            
            # Log the activity
            log_activity(
                'CREATE',
                'recruitment_event',
                event.id,
                f"Event: {event.title} on {event.event_date}",
                f"Added new recruitment event of type: {event.event_type}"
            )
            
            flash('Event added successfully!', 'success')
            return redirect(url_for('calendar'))
        except Exception as e:
            print(f"Error adding event: {e}")
            flash('Error adding event. Please check your input and try again.', 'error')
            db.session.rollback()
    
    try:
        contacts = UniversityContact.query.filter_by(is_active=True).all()
        return render_template('add_event.html', contacts=contacts)
    except Exception as e:
        print(f"Error loading contacts for event form: {e}")
        return render_template('add_event.html', contacts=[])

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    backup_files = get_backup_files()
    return render_template('admin.html', users=users, backup_files=backup_files)

@app.route('/admin/database')
def database_management():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    backup_files = get_backup_files()
    return render_template('database_management.html', backup_files=backup_files)

@app.route('/admin/activity-log')
def activity_log():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get sort parameters
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Define valid sort columns
    valid_sorts = {
        'username': ActivityLog.username,
        'action': ActivityLog.action,
        'table_name': ActivityLog.table_name,
        'created_at': ActivityLog.created_at
    }
    
    # Default to created_at if invalid sort column
    if sort_by not in valid_sorts:
        sort_by = 'created_at'
    
    # Apply sorting and pagination
    if order == 'asc':
        activities = ActivityLog.query.order_by(valid_sorts[sort_by].asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        activities = ActivityLog.query.order_by(valid_sorts[sort_by].desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('activity_log.html', activities=activities, sort_by=sort_by, order=order)

@app.route('/admin/backup', methods=['GET', 'POST'])
def backup():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            backup_filename, backup_path = backup_database()
            if backup_filename:
                flash(f'Database backed up successfully to {backup_filename}', 'success')
                log_activity('BACKUP', 'database', None, f'Database backed up to {backup_filename}', f'Backup created at {backup_path}')
            else:
                flash('Failed to create database backup.', 'error')
        except Exception as e:
            print(f"Error during backup: {e}")
            flash('Error creating database backup. Please check logs.', 'error')
        
        return redirect(url_for('database_management'))
    
    return redirect(url_for('database_management'))

@app.route('/admin/download-backup/<filename>')
def download_backup(filename):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        if os.path.exists(backup_path):
            log_activity('DOWNLOAD_BACKUP', 'database', None, f'Downloaded backup: {filename}')
            return send_file(backup_path, as_attachment=True, download_name=filename)
        else:
            flash('Backup file not found.', 'error')
    except Exception as e:
        print(f"Error downloading backup: {e}")
        flash('Error downloading backup file.', 'error')
    
    return redirect(url_for('database_management'))

@app.route('/admin/restore', methods=['GET', 'POST'])
def restore():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'backup_file' not in request.files:
            flash('No file selected for restore.', 'error')
            return redirect(request.url)
        
        backup_file = request.files['backup_file']
        if backup_file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if backup_file and backup_file.filename.endswith('.db'):
            try:
                # Create a temporary file to hold the uploaded backup
                temp_dir = tempfile.mkdtemp()
                temp_backup_path = os.path.join(temp_dir, backup_file.filename)
                backup_file.save(temp_backup_path)
                
                if restore_database(temp_backup_path):
                    flash('Database restored successfully!', 'success')
                    log_activity('RESTORE', 'database', None, 'Database restored', f'Restored from {backup_file.filename}')
                else:
                    flash('Failed to restore database. Ensure backup file is valid and not corrupted.', 'error')
                    log_activity('RESTORE_FAILED', 'database', None, 'Database restore failed', f'Attempted to restore from {backup_file.filename}')
                
                # Clean up the temporary file
                os.remove(temp_backup_path)
                shutil.rmtree(temp_dir)
                
            except Exception as e:
                print(f"Error during restore: {e}")
                flash('Error restoring database. Please check logs.', 'error')
                log_activity('RESTORE_FAILED', 'database', None, 'Database restore failed', f'Error: {e}')
        else:
            flash('Invalid file type. Please select a .db file.', 'error')
    
    backup_files = get_backup_files()
    return render_template('restore.html', backup_files=backup_files)

# Download routes for data export
@app.route('/download/recruits/<format>')
def download_recruits(format):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    recruits = PotentialRecruit.query.order_by(PotentialRecruit.created_at.desc()).all()
    
    # Prepare data for export
    data = []
    for recruit in recruits:
        data.append({
            'First Name': recruit.first_name,
            'Last Name': recruit.last_name,
            'Email': recruit.email or '',
            'Phone': recruit.phone or '',
            'Major': recruit.major or '',
            'Current School': recruit.current_school,
            'School Type': recruit.school_type,
            'HS Graduation Year': recruit.high_school_graduation_year or '',
            'College Graduation Year': recruit.expected_college_graduation_year or '',
            'GPA': recruit.gpa or '',
            'SAT Score': recruit.sat_score or '',
            'ACT Score': recruit.act_score or '',
            'Interests': recruit.interests or '',
            'Status': recruit.status,
            'Notes': recruit.notes or '',
            'Created Date': utc_to_local(recruit.created_at).strftime('%Y-%m-%d %H:%M:%S') if utc_to_local(recruit.created_at) else '',
            'Last Modified': utc_to_local(recruit.last_modified).strftime('%Y-%m-%d %H:%M:%S') if utc_to_local(recruit.last_modified) else ''
        })
    
    # Log the export activity
    log_activity('EXPORT', 'potential_recruit', None, 'Recruits Export', f'Exported {len(recruits)} recruits to {format.upper()}')
    
    return export_data(data, f'potential_recruits_{datetime.now().strftime("%Y%m%d")}', format, 'Potential Recruits')

@app.route('/download/cadre/<format>')
def download_cadre(format):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cadre_members = Cadre.query.order_by(Cadre.created_at.desc()).all()
    
    # Prepare data for export
    data = []
    for cadre in cadre_members:
        data.append({
            'First Name': cadre.first_name,
            'Last Name': cadre.last_name,
            'Email': cadre.email,
            'Phone': cadre.phone or '',
            'Major': cadre.major,
            'Graduation Year': cadre.graduation_year,
            'Cadet Rank': cadre.cadet_rank,
            'Hometown': cadre.hometown or '',
            'Officer Interest': cadre.officer_interest or '',
            'Status': cadre.status.title(),
            'Unenrollment Date': cadre.unenrollment_date_display or '',
            'Unenrollment Reason': cadre.unenrollment_reason or '',
            'GPA': cadre.gpa or '',
            'Created Date': utc_to_local(cadre.created_at).strftime('%Y-%m-%d %H:%M:%S') if utc_to_local(cadre.created_at) else '',
            'Last Modified': utc_to_local(cadre.last_modified).strftime('%Y-%m-%d %H:%M:%S') if utc_to_local(cadre.last_modified) else ''
        })
    
    # Log the export activity
    log_activity('EXPORT', 'cadre', None, 'Cadre Export', f'Exported {len(cadre_members)} cadre members to {format.upper()}')
    
    return export_data(data, f'cadre_members_{datetime.now().strftime("%Y%m%d")}', format, 'Cadre Members')

@app.route('/download/contacts/<format>')
def download_contacts(format):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    contacts = UniversityContact.query.order_by(UniversityContact.created_at.desc()).all()
    
    # Prepare data for export
    data = []
    for contact in contacts:
        data.append({
            'University Name': contact.university_name,
            'Contact Name': contact.contact_name,
            'Contact Title': contact.contact_title or '',
            'Email': contact.email,
            'Phone': contact.phone or '',
            'Address': contact.address or '',
            'Status': 'Active' if contact.is_active else 'Inactive',
            'Notes': contact.notes or '',
            'Created Date': utc_to_local(contact.created_at).strftime('%Y-%m-%d %H:%M:%S') if utc_to_local(contact.created_at) else '',
            'Last Modified': utc_to_local(contact.last_modified).strftime('%Y-%m-%d %H:%M:%S') if utc_to_local(contact.last_modified) else ''
        })
    
    # Log the export activity
    log_activity('EXPORT', 'university_contact', None, 'Contacts Export', f'Exported {len(contacts)} contacts to {format.upper()}')
    
    return export_data(data, f'high_school_contacts_{datetime.now().strftime("%Y%m%d")}', format, 'High School Contacts')

@app.route('/download/activity-log/<format>')
def download_activity_log(format):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).all()
    
    # Prepare data for export
    data = []
    for activity in activities:
        # Convert UTC time to local time
        local_time = utc_to_local(activity.created_at)
        data.append({
            'Date & Time': local_time.strftime('%Y-%m-%d %H:%M:%S') if local_time else '',
            'Username': activity.username,
            'Action': activity.action,
            'Table': activity.table_name.replace('_', ' ').title() if activity.table_name else '',
            'Record Description': activity.record_description or '',
            'Details': activity.details or '',
            'IP Address': activity.ip_address,
            'User Agent': activity.user_agent
        })
    
    # Log the export activity
    log_activity('EXPORT', 'activity_log', None, 'Activity Log Export', f'Exported {len(activities)} activity logs to {format.upper()}')
    
    return export_data(data, f'activity_log_{datetime.now().strftime("%Y%m%d")}', format, 'Activity Log')

def export_data(data, filename, format, title):
    """Helper function to export data in different formats"""
    if format == 'csv':
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{filename}.csv'
        )
    
    elif format == 'excel':
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=title, index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{filename}.xlsx'
        )
    
    elif format == 'pdf':
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title_para = Paragraph(f"<h1>{title}</h1>", styles['Title'])
        elements.append(title_para)
        elements.append(Paragraph("<br/>", styles['Normal']))
        
        # Prepare table data
        if data:
            headers = list(data[0].keys())
            table_data = [headers]  # Header row
            
            for row in data:
                table_data.append([str(value) for value in row.values()])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(table)
        
        doc.build(elements)
        output.seek(0)
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{filename}.pdf'
        )
    
    else:
        flash('Invalid format specified', 'error')
        return redirect(url_for('dashboard'))

# API endpoints for AJAX requests
@app.route('/api/recruits')
def api_recruits():
    recruits = PotentialRecruit.query.all()
    return jsonify([{
        'id': r.id,
        'name': f"{r.first_name} {r.last_name}",
        'school': r.current_school,
        'status': r.status,
        'created_at': r.created_at.strftime('%Y-%m-%d')
    } for r in recruits])

@app.route('/api/cadre')
def api_cadre():
    cadre = Cadre.query.all()
    return jsonify([{
        'id': c.id,
        'name': f"{c.first_name} {c.last_name}",
        'rank': c.cadet_rank,
        'major': c.major,
        'graduation_year': c.graduation_year,
        'status': c.status
    } for c in cadre])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@afrotc695.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username=admin, password=admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 