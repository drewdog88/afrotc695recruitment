#!/usr/bin/env python3
"""
Production WSGI file for Namecheap/cPanel hosting.
This file handles the Flask application startup for Passenger/Apache.
"""

import os
import sys

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Import your Flask application
from app_production import app as application

if __name__ == "__main__":
    application.run()