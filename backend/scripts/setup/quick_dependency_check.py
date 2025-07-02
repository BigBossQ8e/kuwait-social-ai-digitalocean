#!/usr/bin/env python3
"""
Quick visual dependency checker for Flask app
Shows a color-coded table of dependency status
"""

import subprocess
import sys
import importlib.metadata
from tabulate import tabulate
from datetime import datetime
try:
    from packaging import version
except ImportError:
    version = None

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def get_version(package):
    """Get installed version of a package"""
    try:
        return importlib.metadata.version(package)
    except:
        return None

def check_flask_app():
    """Quick check if Flask app can be imported"""
    try:
        from app_factory import create_app
        return True, "✅ OK"
    except ImportError as e:
        return False, f"❌ {str(e)}"
    except Exception as e:
        return False, f"❌ {str(e)}"

def main():
    print(f"\n{BLUE}🔍 Kuwait Social AI - Quick Dependency Check{RESET}")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python {sys.version.split()[0]}")
    print("=" * 70)
    
    # Define packages to check with categories
    packages = {
        "Core Flask": [
            ("Flask", "3.0.0", True),
            ("Werkzeug", "3.0.0", True),
            ("click", "8.1.0", True),
            ("Jinja2", "3.1.0", True),
        ],
        "Flask Extensions": [
            ("Flask-SQLAlchemy", "3.1.0", True),
            ("Flask-Migrate", "4.0.0", True),
            ("Flask-CORS", "4.0.0", True),
            ("Flask-JWT-Extended", "4.5.0", True),
            ("Flask-Limiter", "3.5.0", False),
            ("Flask-Mail", "0.9.0", False),
            ("Flask-SocketIO", "5.3.0", False),
        ],
        "Database": [
            ("SQLAlchemy", "2.0.0", True),
            ("psycopg2-binary", "2.9.0", True),
            ("alembic", "1.13.0", True),
        ],
        "AI/ML": [
            ("openai", "1.0.0", True),
            ("anthropic", "0.18.0", True),
            ("langchain", "0.1.0", False),
            ("crewai", "0.30.0", False),
        ],
        "Utils": [
            ("redis", "5.0.0", True),
            ("celery", "5.3.0", False),
            ("gunicorn", "21.0.0", True),
            ("python-dotenv", "1.0.0", True),
        ]
    }
    
    # Check each category
    all_good = True
    for category, pkg_list in packages.items():
        print(f"\n{YELLOW}{category}:{RESET}")
        print("-" * 70)
        
        table_data = []
        for pkg_name, min_version, required in pkg_list:
            installed = get_version(pkg_name)
            
            if installed:
                status = f"{GREEN}✅ Installed{RESET}"
                version_str = installed
                # Use proper version comparison
                try:
                    from packaging import version
                    if min_version and version.parse(installed) < version.parse(min_version):
                        status = f"{YELLOW}⚠️  Outdated{RESET}"
                        all_good = False
                except:
                    # Fallback to string comparison if packaging not available
                    if min_version and installed < min_version:
                        status = f"{YELLOW}⚠️  Outdated{RESET}"
                        all_good = False
            else:
                if required:
                    status = f"{RED}❌ Missing{RESET}"
                    all_good = False
                else:
                    status = f"{YELLOW}⚪ Optional{RESET}"
                version_str = "-"
            
            table_data.append([
                pkg_name,
                version_str,
                min_version,
                status,
                "Required" if required else "Optional"
            ])
        
        print(tabulate(table_data, 
                      headers=["Package", "Installed", "Min Version", "Status", "Priority"],
                      tablefmt="grid"))
    
    # Check if Flask app can be imported
    print(f"\n{YELLOW}Flask App Import Test:{RESET}")
    print("-" * 70)
    app_ok, app_msg = check_flask_app()
    print(f"App Factory Import: {app_msg}")
    
    # Summary
    print(f"\n{YELLOW}Summary:{RESET}")
    print("=" * 70)
    if all_good and app_ok:
        print(f"{GREEN}✅ All required dependencies are installed and Flask app can be imported!{RESET}")
    else:
        print(f"{RED}❌ Some issues found. Please install missing dependencies.{RESET}")
        print(f"\n💡 Quick fix: pip install -r requirements.txt")
    
    # Save simple report
    with open("dependency_status.txt", "w") as f:
        f.write(f"Dependency Check - {datetime.now()}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"All dependencies OK: {all_good}\n")
        f.write(f"Flask app imports: {app_ok}\n")
    
    print(f"\n📄 Report saved to: dependency_status.txt")

if __name__ == "__main__":
    main()