#!/usr/bin/env python3
"""
AFROTC 695 Safe Restore System
Simple, safe database restoration from R2 backups
"""

import os
import sys
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get connection to production database"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL not found")
        sys.exit(1)
    
    # Convert postgres:// to postgresql:// for psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)

def get_r2_client():
    """Get R2 client for backup access"""
    try:
        import boto3
        return boto3.client(
            's3',
            endpoint_url=f'https://{os.getenv("CLOUDFLARE_R2_ACCOUNT_ID")}.r2.cloudflarestorage.com',
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
            region_name='auto'
        )
    except Exception as e:
        print(f"❌ Error creating R2 client: {e}")
        return None

def list_backups():
    """List available backups from R2"""
    r2_client = get_r2_client()
    if not r2_client:
        return []
    
    try:
        response = r2_client.list_objects_v2(Bucket='afrotc695recruitment')
        backup_files = []
        
        for obj in response.get('Contents', []):
            filename = obj['Key']
            if filename.endswith('.json') and 'backup' in filename:
                backup_files.append({
                    'filename': filename,
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })
        
        # Sort by last modified (newest first)
        backup_files.sort(key=lambda x: x['LastModified'], reverse=True)
        return backup_files
        
    except Exception as e:
        print(f"❌ Error listing backups: {e}")
        return []

def download_backup(filename):
    """Download backup file from R2"""
    r2_client = get_r2_client()
    if not r2_client:
        return None
    
    try:
        response = r2_client.get_object(Bucket='afrotc695recruitment', Key=filename)
        content = response['Body'].read()
        return json.loads(content.decode('utf-8'))
    except Exception as e:
        print(f"❌ Error downloading backup {filename}: {e}")
        return None

def create_safety_backup():
    """Create a safety backup before restore"""
    print("📸 Creating safety backup...")
    
    # Import backup function from existing system
    try:
        from neon_backup_scheduler import backup_database_neon
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        description = f"Safety backup before restore - {timestamp}"
        
        backup_filename, _ = backup_database_neon(description, "emergency")
        if backup_filename:
            print(f"✅ Safety backup created: {backup_filename}")
            return backup_filename
        else:
            print("❌ Failed to create safety backup")
            return None
    except Exception as e:
        print(f"❌ Error creating safety backup: {e}")
        return None

def confirm_restore(backup_data):
    """Get user confirmation for restore"""
    print("\n🚨 RESTORE CONFIRMATION")
    print("=" * 50)
    print(f"Backup: {backup_data.get('description', 'Unknown')}")
    print(f"Created: {backup_data.get('created_at', 'Unknown')}")
    print(f"Type: {backup_data.get('backup_type', 'Unknown')}")
    
    total_records = sum(len(records) for records in backup_data['tables'].values())
    print(f"Total records: {total_records}")
    
    print("\nTables to restore:")
    for table_name, records in backup_data['tables'].items():
        print(f"  - {table_name}: {len(records)} records")
    
    print("\n⚠️  This will overwrite current data!")
    response = input("Type 'RESTORE' to continue: ")
    
    return response == 'RESTORE'

def restore_data(backup_data):
    """Restore data from backup"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Define restore order (independent tables first)
        restore_order = [
            'user',
            'potential_recruit', 
            'cadet',
            'university_contact',
            'recruitment_event',
            'external_link',
            'recruitment_document',
            'activity_log',
            'password_history'
        ]
        
        restored_count = 0
        
        for table_name in restore_order:
            if table_name not in backup_data['tables']:
                print(f"⏭️  Skipping {table_name} (not in backup)")
                continue
            
            records = backup_data['tables'][table_name]
            if not records:
                print(f"⏭️  Skipping {table_name} (no data)")
                continue
            
            print(f"🔄 Restoring {table_name}: {len(records)} records")
            
            # Clear existing data
            cursor.execute(f'DELETE FROM "{table_name}"')
            
            # Insert new records
            success_count = 0
            for record in records:
                try:
                    columns = list(record.keys())
                    values = list(record.values())
                    placeholders = ', '.join(['%s'] * len(values))
                    column_list = ', '.join([f'"{col}"' for col in columns])
                    
                    query = f'INSERT INTO "{table_name}" ({column_list}) VALUES ({placeholders})'
                    cursor.execute(query, values)
                    success_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error inserting record: {e}")
                    continue
            
            print(f"   ✅ Restored {success_count}/{len(records)} records")
            restored_count += success_count
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Restore completed! {restored_count} records restored")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Main restore function"""
    print("🔄 AFROTC 695 Safe Restore System")
    print("=" * 50)
    
    # List available backups
    print("📂 Available Backups:")
    backup_files = list_backups()
    
    if not backup_files:
        print("❌ No backup files found")
        return
    
    for i, backup in enumerate(backup_files[:10], 1):  # Show last 10
        print(f"{i}. {backup['filename']}")
        print(f"   📅 {backup['last_modified']} | 📦 {backup['size']} bytes")
    
    # Get user selection
    try:
        choice = int(input(f"\nSelect backup (1-{min(10, len(backup_files))}): ")) - 1
        if choice < 0 or choice >= len(backup_files):
            print("❌ Invalid selection")
            return
        
        selected_backup = backup_files[choice]
    except ValueError:
        print("❌ Invalid input")
        return
    
    # Download and validate backup
    print(f"\n📥 Downloading {selected_backup['filename']}...")
    backup_data = download_backup(selected_backup['filename'])
    
    if not backup_data:
        print("❌ Failed to download backup")
        return
    
    # Confirm restore
    if not confirm_restore(backup_data):
        print("❌ Restore cancelled")
        return
    
    # Create safety backup
    safety_backup = create_safety_backup()
    if not safety_backup:
        print("❌ Cannot proceed without safety backup")
        return
    
    # Execute restore
    print("\n🔄 Executing restore...")
    success = restore_data(backup_data)
    
    if success:
        print(f"\n✅ Restore completed successfully!")
        print(f"📸 Safety backup: {safety_backup}")
    else:
        print(f"\n❌ Restore failed!")
        print(f"📸 Safety backup available: {safety_backup}")

if __name__ == "__main__":
    main()
