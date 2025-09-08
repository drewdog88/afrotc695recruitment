"""
Vercel Cron Job for Backup Cleanup
Runs daily at 4:00 AM UTC (9:00 PM PST) to clean up old backup files
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
    """Vercel serverless function handler for backup cleanup"""
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
        
        print('Backup cleanup cron job started:', datetime.now().isoformat())

        # Import the cleanup function from neon_backup_scheduler
        try:
            from neon_backup_scheduler import cleanup_old_backups
            print("Successfully imported cleanup_old_backups")
        except ImportError as e:
            print(f"Import error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': f'Failed to import cleanup function: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                })
            }

        # Run cleanup
        cleanup_old_backups()

        print("Backup cleanup completed successfully")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'Backup cleanup completed successfully',
                'timestamp': datetime.now().isoformat()
            })
        }

    except Exception as e:
        print(f"Backup cleanup error: {e}")
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
