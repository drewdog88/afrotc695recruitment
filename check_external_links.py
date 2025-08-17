#!/usr/bin/env python3
"""
Check and restore external links from backup
"""

import os
import sys
import json
from dotenv import load_dotenv
import psycopg2
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

def check_current_external_links():
    """Check current external links in database"""
    print("=== Current External Links ===")
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM external_link")
        count = cursor.fetchone()[0]
        print(f"Current external links: {count}")

        if count > 0:
            cursor.execute("""
                SELECT id, title, url, description, category, is_active, sort_order, created_at, last_modified
                FROM external_link
                ORDER BY sort_order, title
            """)
            links = cursor.fetchall()

            for link in links:
                link_id, title, url, description, category, is_active, sort_order, created_at, last_modified = link
                print(f"  ID {link_id}: {title}")
                print(f"    URL: {url}")
                print(f"    Category: {category}")
                print(f"    Active: {is_active}")
                print(f"    Sort Order: {sort_order}")
        else:
            print("No external links found in database")

        cursor.close()
        conn.close()
        return count

    except Exception as e:
        print(f"❌ Error checking external links: {e}")
        return 0

def restore_external_links():
    """Restore external links from backup"""
    print("\n=== Restoring External Links from Backup ===")

    # Load backup data
    try:
        with open('backups/neon_backup_20250807_145537.json', 'r') as f:
            backup_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading backup file: {e}")
        return False

    # Get external_link data from backup - correct structure
    external_links_table = backup_data.get('tables', {}).get('external_link', {})
    external_links = external_links_table.get('data', [])
    print(f"Found {len(external_links)} external links in backup")

    if not external_links:
        print("No external links found in backup")
        return False

    # Connect to database
    conn = get_database_connection()
    cursor = conn.cursor()

    try:
        # Clear existing external links
        cursor.execute("DELETE FROM external_link")
        print("✓ Cleared existing external links")

        # Restore external links from backup
        for link_data in external_links:
            try:
                # Map backup fields to current schema
                link_record = {
                    'id': link_data.get('id'),
                    'title': link_data.get('title'),
                    'url': link_data.get('url'),
                    'description': link_data.get('description'),
                    'category': link_data.get('category', 'general'),
                    'is_active': True,  # Default to active
                    'sort_order': 0,    # Default sort order
                    'created_at': datetime.now(),
                    'last_modified': datetime.now()
                }

                cursor.execute("""
                    INSERT INTO external_link (
                        id, title, url, description, category, is_active, sort_order, created_at, last_modified
                    ) VALUES (
                        %(id)s, %(title)s, %(url)s, %(description)s, %(category)s, %(is_active)s, %(sort_order)s, %(created_at)s, %(last_modified)s
                    )
                """, link_record)

                print(f"✓ Restored: {link_record['title']} ({link_record['url']})")

            except Exception as e:
                print(f"⚠ Error restoring link {link_data.get('title', 'unknown')}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n✅ Successfully restored {len(external_links)} external links!")
        return True

    except Exception as e:
        print(f"❌ Error restoring external links: {e}")
        return False

def main():
    """Main function"""
    print("=== External Links Restoration ===")

    # Check current state
    current_count = check_current_external_links()

    # Restore from backup
    if restore_external_links():
        # Verify restoration
        print("\n=== Verification ===")
        final_count = check_current_external_links()

        if final_count > current_count:
            print(f"\n✅ Success! External links restored: {current_count} → {final_count}")
        else:
            print(f"\n⚠ Warning: External link count unchanged: {current_count} → {final_count}")
    else:
        print("\n❌ Failed to restore external links")

if __name__ == "__main__":
    main()
