# Serverless entry point for Vercel CRON backup

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Flask

app = Flask(__name__)

@app.route('/')
def backup_handler():
    """Handle the CRON backup request"""
    try:
        return {
            'success': True,
            'message': 'CRON function is working',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    app.run()