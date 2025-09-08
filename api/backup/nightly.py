# Vercel CRON function for nightly backup
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def handler(request):
    """Vercel serverless function handler for nightly backup"""
    try:
        # Import the backup function from the main app
        from neon_backup_scheduler import backup_database_neon

        print(f"Nightly backup CRON started at {datetime.now().isoformat()}")

        # Run the backup
        backup_filename, backup_url = backup_database_neon("Nightly automatic backup")

        if backup_filename:
            print(f"Nightly backup completed: {backup_filename}")
            return {
                'statusCode': 200,
                'body': {
                    'success': True,
                    'backup_filename': backup_filename,
                    'backup_url': backup_url,
                    'timestamp': datetime.now().isoformat()
                }
            }
        else:
            print("Nightly backup failed")
            return {
                'statusCode': 500,
                'body': {
                    'success': False,
                    'error': 'Backup failed',
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
