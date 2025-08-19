#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def check_schema():
    database_url = os.getenv('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    # Check recruitment_document table
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'recruitment_document' ORDER BY ordinal_position")
    columns = [row[0] for row in cursor.fetchall()]
    print("recruitment_document columns:", columns)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_schema()
