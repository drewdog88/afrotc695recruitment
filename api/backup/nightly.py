"""
Vercel Cron Job for Nightly Database Backup
Runs daily at 2:00 AM UTC (7:00 PM PST) to create daily backups
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def handler(request):
    """Vercel serverless function handler for nightly backup"""
    try:
        # Security validation - verify this is actually a Vercel cron request
        if request.method != 'GET':
            return {
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Method Not Allowed',
                    'timestamp': datetime.now().isoformat()
                })
            }

        # Validate User-Agent
        user_agent = request.headers.get('User-Agent', '')
        if user_agent != 'vercel-cron/1.0':
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Forbidden - Invalid User-Agent',
                    'timestamp': datetime.now().isoformat()
                })
            }

        # Validate CRON_SECRET
        cron_secret = os.getenv('CRON_SECRET')
        if not cron_secret:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'CRON_SECRET not configured',
                    'timestamp': datetime.now().isoformat()
                })
            }

        auth_header = request.headers.get('Authorization', '')
        expected_auth = f'Bearer {cron_secret}'
        if auth_header != expected_auth:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Unauthorized - Invalid CRON_SECRET',
                    'timestamp': datetime.now().isoformat()
                })
            }

        print('Nightly backup cron job started:', datetime.now().isoformat())

        # Create backup directly in the function to avoid import issues
        try:
            import boto3
            from sqlalchemy import create_engine, text
            from urllib.parse import urlparse
            
            # Get database URL
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': False,
                        'error': 'DATABASE_URL not configured',
                        'timestamp': datetime.now().isoformat()
                    })
                }
            
            # Convert postgres:// to postgresql:// for SQLAlchemy
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            # Create database connection
            engine = create_engine(database_url)
            
            # Get R2 client
            r2_client = boto3.client(
                's3',
                endpoint_url='https://kre9xoivjggj03of.public.blob.vercel-storage.com',
                aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
                region_name='auto'
            )
            
            # Create backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'afrotc695_backup_{timestamp}.json'
            
            # Export database data
            with engine.connect() as conn:
                # Get all table names
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
                tables = [row[0] for row in result]
                
                backup_data = {}
                for table in tables:
                    result = conn.execute(text(f"SELECT * FROM {table}"))
                    rows = result.fetchall()
                    columns = result.keys()
                    backup_data[table] = [dict(zip(columns, row)) for row in rows]
            
            # Upload to R2
            backup_json = json.dumps(backup_data, indent=2, default=str)
            r2_client.put_object(
                Bucket='afrotc695-backups',
                Key=backup_filename,
                Body=backup_json,
                ContentType='application/json'
            )
            
            backup_url = f"https://kre9xoivjggj03of.public.blob.vercel-storage.com/afrotc695-backups/{backup_filename}"
            
        except Exception as e:
            print(f"Backup creation error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': f'Backup creation failed: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                })
            }

        if backup_filename:
            print(f"Nightly backup completed successfully: {backup_filename}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Nightly backup completed successfully',
                    'backup_filename': backup_filename,
                    'backup_url': backup_url,
                    'timestamp': datetime.now().isoformat()
                })
            }
        else:
            print("Nightly backup failed")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Backup creation failed',
                    'timestamp': datetime.now().isoformat()
                })
            }

    except Exception as e:
        print(f"Nightly backup error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

# For Vercel serverless functions
def main(request):
    return handler(request)
