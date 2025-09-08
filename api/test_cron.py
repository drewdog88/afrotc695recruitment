# Simple test CRON function
from datetime import datetime

def handler(request):
    return {
        'statusCode': 200,
        'body': {
            'success': True,
            'message': 'Test CRON function working',
            'timestamp': datetime.now().isoformat()
        }
    }
