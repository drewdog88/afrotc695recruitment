#!/usr/bin/env python3
"""
Check current state of documents in the database
"""

import os
import sys
from sqlalchemy import create_engine, text

try:
    from dotenv import load_dotenv
    load_dotenv()
    if os.path.exists("env.local"):
        load_dotenv("env.local")
except ImportError:
    pass


def get_database_engine():
    """Get database engine"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)

        if not database_url:
            print("Error: DATABASE_URL environment variable not set")
            return None

        engine = create_engine(database_url)
        return engine
    except Exception as e:
        print(f"Error creating database engine: {e}")
        return None


def check_documents():
    """Check documents in the database"""
    engine = get_database_engine()
    if not engine:
        return

    try:
        with engine.connect() as connection:
            # Get all documents
            result = connection.execute(text('SELECT id, title, filename, original_filename, blob_url, is_active FROM "recruitment_document" ORDER BY id'))
            documents = result.fetchall()

            print(f"Found {len(documents)} documents in database:")
            print("=" * 80)

            for doc in documents:
                doc_id, title, filename, original_filename, blob_url, is_active = doc
                status = "Active" if is_active else "Inactive"
                has_blob = "Yes" if blob_url else "No"

                print(f"ID: {doc_id}")
                print(f"Title: {title}")
                print(f"Original Filename: {original_filename}")
                print(f"Has Blob URL: {has_blob}")
                print(f"Status: {status}")
                if blob_url:
                    print(f"Blob URL: {blob_url}")
                print("-" * 40)

    except Exception as e:
        print(f"Error checking documents: {e}")


if __name__ == "__main__":
    check_documents()
