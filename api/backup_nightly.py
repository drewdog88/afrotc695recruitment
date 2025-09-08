# Serverless entry point for Vercel CRON backup

import sys
import os

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app from the main app.py
from app import app

# Add a route for the backup
@app.route('/api/backup_nightly')
def backup_handler():
    """Handle the CRON backup request"""
    from datetime import datetime
    from flask import jsonify
    
    try:
        return jsonify({
            'success': True,
            'message': 'CRON function is working',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Export the app for Vercel
if __name__ == '__main__':
    app.run()