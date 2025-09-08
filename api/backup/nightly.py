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

        # Simple test first - just return success to verify the function works
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'CRON function is working - test successful',
                'timestamp': datetime.now().isoformat(),
                'env_check': {
                    'DATABASE_URL_set': bool(os.getenv('DATABASE_URL')),
                    'R2_ACCESS_KEY_set': bool(os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')),
                    'R2_SECRET_set': bool(os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'))
                }
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
