"""
Vercel Cron Job for Nightly Database Backup
Runs daily at 2:00 AM UTC (7:00 PM PST) to create daily backups
"""

import os
import json
from datetime import datetime

def handler(request):
    """Vercel serverless function handler for nightly backup"""
    try:
        print('Nightly backup cron job started:', datetime.now().isoformat())
        
        # Simple test - just return success
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'CRON function is working - test successful',
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