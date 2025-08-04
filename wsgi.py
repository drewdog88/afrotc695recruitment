#!/usr/bin/env python3
"""
WSGI entry point for AFROTC 695 Recruitment Management System
Production deployment configuration
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the Flask app
from app_production import app

if __name__ == "__main__":
    app.run() 