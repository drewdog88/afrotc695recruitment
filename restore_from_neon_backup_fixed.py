#!/usr/bin/env python3
"""
Script to restore data from Neon backup with proper PostgreSQL syntax and schema mapping
"""

import os
import sys
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from datetime import datetime

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get connection to production database"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        sys.exit(1)

    # Convert postgres:// to postgresql:// for psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def load_backup_data():
    """Load the latest backup data"""
    backup_file = "backups/neon_backup_20250807_145537.json"

    if not os.path.exists(backup_file):
        print(f"Error: Backup file {backup_file} not found")
        sys.exit(1)

    try:
        with open(backup_file, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading backup data: {e}")
        sys.exit(1)

def clear_existing_data(conn):
    """Clear existing data from all tables"""
    cursor = conn.cursor()

    print("Clearing existing data...")

    # Clear tables in reverse dependency order
    tables = [
        'activity_log',
        'password_history',
        'recruitment_document',
        'external_link',
        'recruitment_event',
        'university_contact',
        'cadet',
        'potential_recruit',
        'user'
    ]

    for table in tables:
        try:
            cursor.execute(f'DELETE FROM "{table}"')
            print(f"✓ Cleared {table}")
        except Exception as e:
            print(f"⚠ Error clearing {table}: {e}")

    # Reset sequences
    sequences = [
        'user_id_seq',
        'potential_recruit_id_seq',
        'cadet_id_seq',
        'university_contact_id_seq',
        'recruitment_event_id_seq',
        'external_link_id_seq',
        'recruitment_document_id_seq',
        'password_history_id_seq',
        'activity_log_id_seq'
    ]

    for seq in sequences:
        try:
            cursor.execute(f'ALTER SEQUENCE "{seq}" RESTART WITH 1')
            print(f"✓ Reset sequence {seq}")
        except Exception as e:
            print(f"⚠ Error resetting {seq}: {e}")

    conn.commit()
    cursor.close()

def restore_users(conn, users_data):
    """Restore users with proper PostgreSQL syntax"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(users_data)} users...")

    for user in users_data:
        try:
            # Map backup fields to current schema
            user_data = {
                'id': user.get('id'),
                'username': user.get('username'),
                'email': user.get('email'),
                'password_hash': user.get('password_hash'),
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'phone': user.get('phone'),
                'role': user.get('role'),
                'is_active': user.get('is_active'),
                'is_locked': user.get('is_locked'),
                'failed_login_attempts': user.get('failed_login_attempts', 0),
                'password_changed_at': user.get('password_changed_at'),
                'password_expires_at': user.get('password_expires_at'),
                'force_password_change': user.get('force_password_change', False),
                'secret_question': user.get('secret_question'),
                'secret_answer_hash': user.get('secret_answer_hash'),
                'last_modified': user.get('last_modified')
            }

            cursor.execute("""
                INSERT INTO "user" (
                    id, username, email, password_hash, first_name, last_name,
                    phone, role, is_active, is_locked, failed_login_attempts,
                    password_changed_at, password_expires_at, force_password_change,
                    secret_question, secret_answer_hash, last_modified
                ) VALUES (
                    %(id)s, %(username)s, %(email)s, %(password_hash)s, %(first_name)s, %(last_name)s,
                    %(phone)s, %(role)s, %(is_active)s, %(is_locked)s, %(failed_login_attempts)s,
                    %(password_changed_at)s, %(password_expires_at)s, %(force_password_change)s,
                    %(secret_question)s, %(secret_answer_hash)s, %(last_modified)s
                ) ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    email = EXCLUDED.email,
                    password_hash = EXCLUDED.password_hash,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    phone = EXCLUDED.phone,
                    role = EXCLUDED.role,
                    is_active = EXCLUDED.is_active,
                    is_locked = EXCLUDED.is_locked,
                    failed_login_attempts = EXCLUDED.failed_login_attempts,
                    password_changed_at = EXCLUDED.password_changed_at,
                    password_expires_at = EXCLUDED.password_expires_at,
                    force_password_change = EXCLUDED.force_password_change,
                    secret_question = EXCLUDED.secret_question,
                    secret_answer_hash = EXCLUDED.secret_answer_hash,
                    last_modified = EXCLUDED.last_modified
            """, user_data)
            print(f"✓ Restored user {user['username']}")
        except Exception as e:
            print(f"⚠ Error restoring user {user.get('username', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def restore_cadets(conn, cadets_data):
    """Restore cadets with proper schema mapping"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(cadets_data)} cadets...")

    for cadet in cadets_data:
        try:
            # Map backup fields to current schema
            cadet_data = {
                'id': cadet.get('id'),
                'first_name': cadet.get('first_name'),
                'last_name': cadet.get('last_name'),
                'email': cadet.get('email'),
                'phone': cadet.get('phone'),
                'cadet_rank': cadet.get('rank'),  # Map 'rank' to 'cadet_rank'
                'graduation_year': cadet.get('class_year'),  # Map 'class_year' to 'graduation_year'
                'major': cadet.get('major'),
                'gpa': cadet.get('gpa'),
                'status': cadet.get('status'),
                'hometown': None,  # Not in backup, set to None
                'officer_interest': None,  # Not in backup, set to None
                'unenrollment_reason': None,  # Not in backup, set to None
                'unenrollment_date': None,  # Not in backup, set to None
                'created_at': cadet.get('created_at'),
                'last_modified': cadet.get('updated_at')  # Map 'updated_at' to 'last_modified'
            }

            cursor.execute("""
                INSERT INTO cadet (
                    id, first_name, last_name, email, phone, cadet_rank, graduation_year,
                    major, gpa, status, hometown, officer_interest, unenrollment_reason,
                    unenrollment_date, created_at, last_modified
                ) VALUES (
                    %(id)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(cadet_rank)s, %(graduation_year)s,
                    %(major)s, %(gpa)s, %(status)s, %(hometown)s, %(officer_interest)s, %(unenrollment_reason)s,
                    %(unenrollment_date)s, %(created_at)s, %(last_modified)s
                ) ON CONFLICT (id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    cadet_rank = EXCLUDED.cadet_rank,
                    graduation_year = EXCLUDED.graduation_year,
                    major = EXCLUDED.major,
                    gpa = EXCLUDED.gpa,
                    status = EXCLUDED.status,
                    hometown = EXCLUDED.hometown,
                    officer_interest = EXCLUDED.officer_interest,
                    unenrollment_reason = EXCLUDED.unenrollment_reason,
                    unenrollment_date = EXCLUDED.unenrollment_date,
                    created_at = EXCLUDED.created_at,
                    last_modified = EXCLUDED.last_modified
            """, cadet_data)
            print(f"✓ Restored cadet {cadet['first_name']} {cadet['last_name']}")
        except Exception as e:
            print(f"⚠ Error restoring cadet {cadet.get('first_name', 'unknown')} {cadet.get('last_name', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def restore_potential_recruits(conn, recruits_data):
    """Restore potential recruits"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(recruits_data)} potential recruits...")

    for recruit in recruits_data:
        try:
            cursor.execute("""
                INSERT INTO potential_recruit (
                    id, first_name, last_name, email, phone, school, grade_level,
                    gpa, interests, status, notes, created_at, updated_at
                ) VALUES (
                    %(id)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(school)s, %(grade_level)s,
                    %(gpa)s, %(interests)s, %(status)s, %(notes)s, %(created_at)s, %(updated_at)s
                ) ON CONFLICT (id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    school = EXCLUDED.school,
                    grade_level = EXCLUDED.grade_level,
                    gpa = EXCLUDED.gpa,
                    interests = EXCLUDED.interests,
                    status = EXCLUDED.status,
                    notes = EXCLUDED.notes,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
            """, recruit)
            print(f"✓ Restored recruit {recruit['first_name']} {recruit['last_name']}")
        except Exception as e:
            print(f"⚠ Error restoring recruit {recruit.get('first_name', 'unknown')} {recruit.get('last_name', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def restore_university_contacts(conn, contacts_data):
    """Restore university contacts"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(contacts_data)} university contacts...")

    for contact in contacts_data:
        try:
            cursor.execute("""
                INSERT INTO university_contact (
                    id, name, title, email, phone, school, department,
                    notes, created_at, updated_at
                ) VALUES (
                    %(id)s, %(name)s, %(title)s, %(email)s, %(phone)s, %(school)s, %(department)s,
                    %(notes)s, %(created_at)s, %(updated_at)s
                ) ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    title = EXCLUDED.title,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    school = EXCLUDED.school,
                    department = EXCLUDED.department,
                    notes = EXCLUDED.notes,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
            """, contact)
            print(f"✓ Restored contact {contact['name']}")
        except Exception as e:
            print(f"⚠ Error restoring contact {contact.get('name', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def restore_recruitment_events(conn, events_data):
    """Restore recruitment events"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(events_data)} recruitment events...")

    for event in events_data:
        try:
            cursor.execute("""
                INSERT INTO recruitment_event (
                    id, title, description, event_date, event_type, location,
                    status, notes, created_at, updated_at
                ) VALUES (
                    %(id)s, %(title)s, %(description)s, %(event_date)s, %(event_type)s, %(location)s,
                    %(status)s, %(notes)s, %(created_at)s, %(updated_at)s
                ) ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    event_date = EXCLUDED.event_date,
                    event_type = EXCLUDED.event_type,
                    location = EXCLUDED.location,
                    status = EXCLUDED.status,
                    notes = EXCLUDED.notes,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
            """, event)
            print(f"✓ Restored event {event['title']}")
        except Exception as e:
            print(f"⚠ Error restoring event {event.get('title', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def restore_external_links(conn, links_data):
    """Restore external links"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(links_data)} external links...")

    for link in links_data:
        try:
            # Remove updated_at field as it doesn't exist in current schema
            link_data = {
                'id': link.get('id'),
                'title': link.get('title'),
                'url': link.get('url'),
                'description': link.get('description'),
                'category': link.get('category'),
                'created_at': link.get('created_at')
            }

            cursor.execute("""
                INSERT INTO external_link (
                    id, title, url, description, category, created_at
                ) VALUES (
                    %(id)s, %(title)s, %(url)s, %(description)s, %(category)s, %(created_at)s
                ) ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    url = EXCLUDED.url,
                    description = EXCLUDED.description,
                    category = EXCLUDED.category,
                    created_at = EXCLUDED.created_at
            """, link_data)
            print(f"✓ Restored link {link['title']}")
        except Exception as e:
            print(f"⚠ Error restoring link {link.get('title', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def restore_recruitment_documents(conn, documents_data):
    """Restore recruitment documents"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(documents_data)} recruitment documents...")

    for doc in documents_data:
        try:
            cursor.execute("""
                INSERT INTO recruitment_document (
                    id, title, description, file_path, file_type, file_size,
                    created_at, updated_at
                ) VALUES (
                    %(id)s, %(title)s, %(description)s, %(file_path)s, %(file_type)s, %(file_size)s,
                    %(created_at)s, %(updated_at)s
                ) ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    file_path = EXCLUDED.file_path,
                    file_type = EXCLUDED.file_type,
                    file_size = EXCLUDED.file_size,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
            """, doc)
            print(f"✓ Restored document {doc['title']}")
        except Exception as e:
            print(f"⚠ Error restoring document {doc.get('title', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def restore_activity_logs(conn, logs_data):
    """Restore activity logs"""
    cursor = conn.cursor()

    print(f"\nRestoring {len(logs_data)} activity logs...")

    for log in logs_data:
        try:
            # Remove username field as it doesn't exist in current schema
            log_data = {
                'id': log.get('id'),
                'user_id': log.get('user_id'),
                'action': log.get('action'),
                'table_name': log.get('table_name'),
                'record_id': log.get('record_id'),
                'record_description': log.get('record_description'),
                'details': log.get('details'),
                'ip_address': log.get('ip_address'),
                'user_agent': log.get('user_agent'),
                'created_at': log.get('created_at')
            }

            cursor.execute("""
                INSERT INTO activity_log (
                    id, user_id, action, table_name, record_id,
                    record_description, details, ip_address, user_agent, created_at
                ) VALUES (
                    %(id)s, %(user_id)s, %(action)s, %(table_name)s, %(record_id)s,
                    %(record_description)s, %(details)s, %(ip_address)s, %(user_agent)s, %(created_at)s
                ) ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    action = EXCLUDED.action,
                    table_name = EXCLUDED.table_name,
                    record_id = EXCLUDED.record_id,
                    record_description = EXCLUDED.record_description,
                    details = EXCLUDED.details,
                    ip_address = EXCLUDED.ip_address,
                    user_agent = EXCLUDED.user_agent,
                    created_at = EXCLUDED.created_at
            """, log_data)
            print(f"✓ Restored activity log {log['id']}")
        except Exception as e:
            print(f"⚠ Error restoring activity log {log.get('id', 'unknown')}: {e}")

    conn.commit()
    cursor.close()

def main():
    """Main restoration function"""
    print("=== Neon Backup Data Restoration (Fixed Schema) ===")

    # Load backup data
    print("Loading backup data...")
    backup_data = load_backup_data()

    # Connect to database
    conn = get_database_connection()

    # Clear existing data
    clear_existing_data(conn)

    # Restore data for each table
    tables_data = backup_data.get('tables', {})

    if 'user' in tables_data:
        restore_users(conn, tables_data['user']['data'])

    if 'cadet' in tables_data:
        restore_cadets(conn, tables_data['cadet']['data'])

    if 'potential_recruit' in tables_data:
        restore_potential_recruits(conn, tables_data['potential_recruit']['data'])

    if 'university_contact' in tables_data:
        restore_university_contacts(conn, tables_data['university_contact']['data'])

    if 'recruitment_event' in tables_data:
        restore_recruitment_events(conn, tables_data['recruitment_event']['data'])

    if 'external_link' in tables_data:
        restore_external_links(conn, tables_data['external_link']['data'])

    if 'recruitment_document' in tables_data:
        restore_recruitment_documents(conn, tables_data['recruitment_document']['data'])

    if 'activity_log' in tables_data:
        restore_activity_logs(conn, tables_data['activity_log']['data'])

    conn.close()

    print("\n=== Data restoration complete ===")
    print("You can now log in to production with your existing credentials!")

if __name__ == "__main__":
    main()
