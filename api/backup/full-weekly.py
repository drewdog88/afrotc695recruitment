"""
Vercel Cron Job for Weekly Full Database Backup
Runs weekly on Sundays at 3:00 AM UTC (8:00 PM PST Saturday) to create full backups
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
    """Vercel serverless function handler for weekly full backup"""
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
        
        print('Weekly full backup cron job started:', datetime.now().isoformat())

        # Import the backup function from neon_backup_scheduler
        try:
            from neon_backup_scheduler import create_full_backup_tgz
            print("Successfully imported create_full_backup_tgz")
        except ImportError as e:
            print(f"Import error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': f'Failed to import backup function: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                })
            }

        # Create full backup
        backup_filename, backup_url = create_full_backup_tgz("Weekly full backup")

        if backup_filename:
            print(f"Weekly full backup completed successfully: {backup_filename}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Weekly full backup completed successfully',
                    'backup_filename': backup_filename,
                    'backup_url': backup_url,
                    'timestamp': datetime.now().isoformat()
                })
            }
        else:
            print("Weekly full backup failed")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Full backup creation failed',
                    'timestamp': datetime.now().isoformat()
                })
            }

    except Exception as e:
        print(f"Weekly full backup error: {e}")
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
