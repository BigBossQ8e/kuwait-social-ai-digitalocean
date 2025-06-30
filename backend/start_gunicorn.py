#!/usr/bin/env python3
"""Start the application using Gunicorn (production-like server)"""

import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Remove MAX_CONTENT_LENGTH from environment to avoid string conversion issue
if 'MAX_CONTENT_LENGTH' in os.environ:
    del os.environ['MAX_CONTENT_LENGTH']

print("=== Starting Kuwait Social AI with Gunicorn ===")
print("API Base URL: http://localhost:8000")
print("\nThis is using Gunicorn, a production-grade WSGI server")
print("Press Ctrl+C to stop the server")
print("=" * 50)

# Start Gunicorn with config file
subprocess.run([
    "gunicorn",
    "--config", "gunicorn_config.py",
    "wsgi:application"
])