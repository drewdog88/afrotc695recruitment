# Serverless entry point for Vercel CRON backup

import json
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def backup_handler():
    """Handle the CRON backup request"""
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

if __name__ == '__main__':
    app.run()
