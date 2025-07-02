#!/usr/bin/env python3
"""
DigitalOcean Deployment Check Script
"""

import os
import subprocess
import json

def check_environment():
    """Check if running on DigitalOcean"""
    print("\n=== Environment Check ===")
    
    # Check for DigitalOcean metadata
    try:
        response = subprocess.run(
            ['curl', '-s', 'http://169.254.169.254/metadata/v1/id'],
            capture_output=True, text=True, timeout=2
        )
        if response.returncode == 0:
            print("✅ Running on DigitalOcean Droplet")
            print(f"   Droplet ID: {response.stdout.strip()}")
        else:
            print("❌ Not running on DigitalOcean")
    except:
        print("❌ Not running on DigitalOcean")
    
    # Check environment variables
    print("\n=== Environment Variables ===")
    important_vars = [
        'DATABASE_URL',
        'REDIS_URL',
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'FLASK_ENV',
        'PORT'
    ]
    
    for var in important_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'SECRET' in var:
                print(f"✅ {var}: ***hidden***")
            else:
                print(f"✅ {var}: {value[:50]}...")
        else:
            print(f"❌ {var}: Not set")

def check_services():
    """Check running services"""
    print("\n=== Service Status ===")
    
    services = ['postgresql', 'redis-server', 'nginx']
    
    for service in services:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service],
                capture_output=True, text=True
            )
            if result.stdout.strip() == 'active':
                print(f"✅ {service}: Running")
            else:
                print(f"❌ {service}: {result.stdout.strip()}")
        except:
            print(f"⚠️  {service}: Unable to check")

def check_app_service():
    """Check if app is running"""
    print("\n=== Application Status ===")
    
    # Check if gunicorn is running
    try:
        result = subprocess.run(['pgrep', '-f', 'gunicorn'], capture_output=True)
        if result.returncode == 0:
            print("✅ Gunicorn is running")
            # Get process details
            subprocess.run(['ps', 'aux', '|', 'grep', 'gunicorn'], shell=True)
        else:
            print("❌ Gunicorn is not running")
    except:
        print("⚠️  Unable to check Gunicorn status")
    
    # Check if app responds
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:5001/api/health'],
            capture_output=True, text=True
        )
        if result.stdout == '200':
            print("✅ Application is responding")
        else:
            print(f"❌ Application returned status: {result.stdout}")
    except:
        print("❌ Application is not responding")

def check_logs():
    """Check recent logs for errors"""
    print("\n=== Recent Logs ===")
    
    log_files = [
        '/var/log/nginx/error.log',
        '/var/log/postgresql/postgresql-*.log',
        'logs/kuwait-social-ai.log'
    ]
    
    for log_file in log_files:
        if '*' in log_file:
            # Handle wildcards
            import glob
            files = glob.glob(log_file)
            if files:
                log_file = files[-1]  # Get most recent
        
        if os.path.exists(log_file):
            print(f"\nChecking {log_file}:")
            try:
                result = subprocess.run(
                    ['tail', '-n', '20', log_file, '|', 'grep', '-i', 'error'],
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    print(result.stdout)
                else:
                    print("No recent errors found")
            except:
                print("Unable to read log file")

if __name__ == "__main__":
    print("DigitalOcean Deployment Check")
    print("=" * 50)
    
    check_environment()
    check_services()
    check_app_service()
    check_logs()
    
    print("\n" + "=" * 50)
    print("Check complete!")
