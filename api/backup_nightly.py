# Vercel CRON function for nightly backup - simplified test
from datetime import datetime

def handler(request):
    """Vercel serverless function handler for nightly backup"""
    try:
        print(f"Nightly backup CRON started at {datetime.now().isoformat()}")
        
        return {
            'statusCode': 200,
            'body': {
                'success': True,
                'message': 'CRON function is working',
                'timestamp': datetime.now().isoformat()
            }
        }
            
    except Exception as e:
        print(f"Error in nightly backup CRON: {e}")
        return {
            'statusCode': 500,
            'body': {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        }