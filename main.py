#!/usr/bin/env python3
"""
LeadLiftr - Professional CRM Data Extraction
Entry point for production deployment
"""

import os
import sys
from simple_app import app

# For gunicorn (production)
# This exposes the Flask app as 'app' for gunicorn to find
application = app

# Make sure required directories exist for production
os.makedirs('config', exist_ok=True)
os.makedirs('exports', exist_ok=True)

if __name__ == "__main__":
    # Get port from environment variable (for deployment platforms)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app in development mode
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )