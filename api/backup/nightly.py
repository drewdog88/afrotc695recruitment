"""
Vercel Cron Job for Nightly Database Backup
"""

import json
from datetime import datetime

def handler(request):
    """Vercel serverless function handler for nightly backup"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'success': True,
            'message': 'CRON function is working',
            'timestamp': datetime.now().isoformat()
        })
    }

def main(request):
    return handler(request)