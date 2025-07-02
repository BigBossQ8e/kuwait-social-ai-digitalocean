#!/usr/bin/env python3
"""
Flask Dependencies Checker for Kuwait Social AI
Checks dependencies on both local and remote servers
"""

import subprocess
import sys
import json
import os
from datetime import datetime
import importlib.metadata
import pkg_resources
from packaging import version

# Core Flask dependencies to check
CORE_DEPENDENCIES = [
    "Flask",
    "Flask-SQLAlchemy", 
    "Flask-Migrate",
    "Flask-CORS",
    "Flask-JWT-Extended",
    "Flask-Limiter",
    "Flask-Mail",
    "Flask-SocketIO",
    "werkzeug",
    "click",
    "itsdangerous",
    "Jinja2",
    "MarkupSafe"
]

# Critical dependencies for the app
CRITICAL_DEPENDENCIES = [
    "SQLAlchemy",
    "alembic",
    "psycopg2-binary",
    "redis",
    "celery",
    "marshmallow",
    "marshmallow-sqlalchemy",
    "python-dotenv",
    "PyJWT",
    "cryptography",
    "gunicorn",
    "gevent"
]

# AI and ML dependencies
AI_DEPENDENCIES = [
    "openai",
    "anthropic",
    "langchain",
    "langchain-openai",
    "langchain-anthropic",
    "langchain-community",
    "crewai"
]

# Optional but important dependencies
OPTIONAL_DEPENDENCIES = [
    "Pillow",
    "opencv-python",
    "deep-translator",
    "langdetect",
    "arabic-reshaper",
    "python-bidi",
    "bleach",
    "python-telegram-bot",
    "APScheduler",
    "sentry-sdk"
]

def get_installed_version(package_name):
    """Get installed version of a package"""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        try:
            # Fallback for older Python versions
            return pkg_resources.get_distribution(package_name).version
        except:
            return None

def check_python_version():
    """Check Python version"""
    py_version = sys.version_info
    py_version_str = f"{py_version.major}.{py_version.minor}.{py_version.micro}"
    
    print(f"\n🐍 Python Version: {py_version_str}")
    
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 9):
        print("❌ Python 3.9+ is required!")
        return False
    elif py_version.major == 3 and py_version.minor == 9:
        print("⚠️  Python 3.9 detected - some AI features require 3.10+")
        return True
    else:
        print("✅ Python version is compatible")
        return True

def check_dependencies(dep_list, category_name):
    """Check a list of dependencies"""
    print(f"\n📦 {category_name}:")
    print("-" * 50)
    
    missing = []
    outdated = []
    installed = []
    
    for package in dep_list:
        version = get_installed_version(package)
        if version:
            installed.append(f"{package}=={version}")
            print(f"✅ {package}: {version}")
        else:
            missing.append(package)
            print(f"❌ {package}: NOT INSTALLED")
    
    return {
        "category": category_name,
        "total": len(dep_list),
        "installed": len(installed),
        "missing": missing,
        "packages": installed
    }

def check_flask_compatibility():
    """Check Flask and Werkzeug compatibility"""
    print("\n🔍 Flask Compatibility Check:")
    print("-" * 50)
    
    flask_version = get_installed_version("Flask")
    werkzeug_version = get_installed_version("werkzeug")
    click_version = get_installed_version("click")
    
    if flask_version and werkzeug_version:
        flask_v = version.parse(flask_version)
        werkzeug_v = version.parse(werkzeug_version)
        
        # Check known compatibility issues
        if flask_v >= version.parse("3.0.0") and werkzeug_v < version.parse("3.0.0"):
            print("❌ Flask 3.x requires Werkzeug 3.x")
            return False
        elif flask_v >= version.parse("3.1.0") and click_version:
            click_v = version.parse(click_version)
            if click_v < version.parse("8.1.7"):
                print("❌ Flask 3.1+ requires click 8.1.7+")
                return False
        
        print(f"✅ Flask {flask_version} and Werkzeug {werkzeug_version} are compatible")
        return True
    else:
        print("❌ Cannot check compatibility - Flask or Werkzeug not installed")
        return False

def generate_pip_freeze():
    """Generate pip freeze output"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                              capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error generating pip freeze: {e}"

def check_requirements_files():
    """Check for requirements files"""
    print("\n📄 Requirements Files:")
    print("-" * 50)
    
    req_files = [
        "requirements.txt",
        "requirements.in", 
        "requirements-dev.txt",
        "requirements-prod.txt"
    ]
    
    found_files = []
    for req_file in req_files:
        if os.path.exists(req_file):
            print(f"✅ Found: {req_file}")
            found_files.append(req_file)
            
            # Check if it's a compiled file
            with open(req_file, 'r') as f:
                first_line = f.readline()
                if "autogenerated by pip-compile" in first_line:
                    print(f"   ℹ️  This is a pip-compile generated file")
        else:
            print(f"❌ Missing: {req_file}")
    
    return found_files

def save_dependency_report(results):
    """Save dependency report to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"dependency_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_file}")
    return report_file

def main():
    """Main function"""
    print("=" * 60)
    print("🔍 Kuwait Social AI - Flask Dependencies Checker")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "environment": "local",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "checks": {}
    }
    
    # Check Python version
    python_ok = check_python_version()
    results["python_compatible"] = python_ok
    
    # Check core Flask dependencies
    results["checks"]["core"] = check_dependencies(CORE_DEPENDENCIES, "Core Flask Dependencies")
    
    # Check critical dependencies
    results["checks"]["critical"] = check_dependencies(CRITICAL_DEPENDENCIES, "Critical Dependencies")
    
    # Check AI dependencies
    results["checks"]["ai"] = check_dependencies(AI_DEPENDENCIES, "AI/ML Dependencies")
    
    # Check optional dependencies
    results["checks"]["optional"] = check_dependencies(OPTIONAL_DEPENDENCIES, "Optional Dependencies")
    
    # Check Flask compatibility
    flask_compatible = check_flask_compatibility()
    results["flask_compatible"] = flask_compatible
    
    # Check requirements files
    req_files = check_requirements_files()
    results["requirements_files"] = req_files
    
    # Generate summary
    print("\n📊 Summary:")
    print("=" * 60)
    
    total_missing = 0
    for category, data in results["checks"].items():
        missing_count = len(data["missing"])
        total_missing += missing_count
        print(f"{data['category']}: {data['installed']}/{data['total']} installed")
        if missing_count > 0:
            print(f"   Missing: {', '.join(data['missing'])}")
    
    print(f"\nTotal missing packages: {total_missing}")
    
    # Save pip freeze
    print("\n📦 Saving current pip freeze...")
    pip_freeze = generate_pip_freeze()
    results["pip_freeze"] = pip_freeze.split('\n')
    
    # Save report
    report_file = save_dependency_report(results)
    
    # Provide recommendations
    print("\n💡 Recommendations:")
    print("-" * 50)
    
    if total_missing > 0:
        print("1. Install missing packages:")
        print("   pip install -r requirements.txt")
    
    if not python_ok or not flask_compatible:
        print("2. Consider upgrading Python to 3.10+ for full compatibility")
    
    if "requirements.in" in req_files:
        print("3. Use pip-compile to regenerate requirements.txt:")
        print("   pip-compile requirements.in")
    
    print("\n✅ Dependency check complete!")
    
    return results

if __name__ == "__main__":
    main()