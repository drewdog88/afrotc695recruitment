#!/usr/bin/env python3
"""Check database status after restore"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def check_database():
    try:
        # Use DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Check users
        cursor.execute('SELECT username, email, role FROM "user"')
        users = cursor.fetchall()
        print(f"Users: {len(users)}")
        for user in users:
            print(f"  • {user[0]} ({user[1]}) - {user[2]}")

        # Check cadets
        cursor.execute('SELECT COUNT(*) FROM cadet')
        cadet_count = cursor.fetchone()[0]
        print(f"Cadets: {cadet_count}")

        # Check contacts
        cursor.execute('SELECT COUNT(*) FROM university_contact')
        contact_count = cursor.fetchone()[0]
        print(f"University Contacts: {contact_count}")

        # Check recruits
        cursor.execute('SELECT COUNT(*) FROM potential_recruit')
        recruit_count = cursor.fetchone()[0]
        print(f"Potential Recruits: {recruit_count}")

        # Check events
        cursor.execute('SELECT COUNT(*) FROM recruitment_event')
        event_count = cursor.fetchone()[0]
        print(f"Recruitment Events: {event_count}")

        # Check documents
        cursor.execute('SELECT COUNT(*) FROM recruitment_document')
        doc_count = cursor.fetchone()[0]
        print(f"Recruitment Documents: {doc_count}")

        # Check external links
        cursor.execute('SELECT COUNT(*) FROM external_link')
        link_count = cursor.fetchone()[0]
        print(f"External Links: {link_count}")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()
