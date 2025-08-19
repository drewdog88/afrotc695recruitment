#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def add_blob_url_column():
    database_url = os.getenv('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    try:
        print("Adding blob_url column to recruitment_document table...")
        cursor.execute("ALTER TABLE recruitment_document ADD COLUMN IF NOT EXISTS blob_url TEXT")
        conn.commit()
        print("✓ blob_url column added successfully")

        # Verify the column was added
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'recruitment_document' ORDER BY ordinal_position")
        columns = [row[0] for row in cursor.fetchall()]
        print("Updated recruitment_document columns:", columns)

    except Exception as e:
        print(f"Error adding column: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_blob_url_column()
