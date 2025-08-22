# Serverless entry point for Vercel
# This file should be minimal to avoid exceeding the 250MB limit

import sys
import os

# Add the parent directory to the path so we can import from the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app from the main app.py
from app import app

# Export the app for Vercel
if __name__ == '__main__':
    app.run()
