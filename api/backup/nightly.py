"""
Vercel Cron Job for Nightly Database Backup
"""

import json
from datetime import datetime

def handler(request):
    """Vercel serverless function handler for nightly backup"""
    try:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'CRON function is working',
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }