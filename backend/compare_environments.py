#!/usr/bin/env python3
"""
Visual comparison of dependencies between local and production environments
"""

import json
import os
from datetime import datetime
from tabulate import tabulate

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

def find_latest_reports():
    """Find the latest dependency reports"""
    import glob
    
    local_reports = sorted(glob.glob("dependency_report_*.json"))
    prod_reports = sorted(glob.glob("production_dependency_report_*.json"))
    
    if not local_reports:
        print(f"{RED}❌ No local dependency report found. Run: python3 check_dependencies.py{RESET}")
        return None, None
        
    if not prod_reports:
        print(f"{RED}❌ No production report found. Run: ./check_remote_dependencies.sh{RESET}")
        return None, None
    
    return local_reports[-1], prod_reports[-1]

def load_report(filename):
    """Load a dependency report"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{RED}Error loading {filename}: {e}{RESET}")
        return None

def compare_packages(local_packages, prod_packages):
    """Compare package lists and return differences"""
    local_dict = {pkg.split('==')[0]: pkg.split('==')[1] 
                  for pkg in local_packages if '==' in pkg}
    prod_dict = {pkg.split('==')[0]: pkg.split('==')[1] 
                 for pkg in prod_packages if '==' in pkg}
    
    all_packages = sorted(set(local_dict.keys()) | set(prod_dict.keys()))
    
    differences = []
    for pkg in all_packages:
        local_ver = local_dict.get(pkg, "Not installed")
        prod_ver = prod_dict.get(pkg, "Not installed")
        
        if local_ver != prod_ver:
            if local_ver == "Not installed":
                status = f"{RED}Missing locally{RESET}"
            elif prod_ver == "Not installed":
                status = f"{YELLOW}Missing in production{RESET}"
            else:
                status = f"{CYAN}Version mismatch{RESET}"
            
            differences.append([pkg, local_ver, prod_ver, status])
    
    return differences

def main():
    print(f"\n{BLUE}🔍 Environment Dependency Comparison{RESET}")
    print("=" * 70)
    
    # Find reports
    local_file, prod_file = find_latest_reports()
    if not local_file or not prod_file:
        return
    
    # Load reports
    local_report = load_report(local_file)
    prod_report = load_report(prod_file)
    
    if not local_report or not prod_report:
        return
    
    # Basic info
    print(f"\n{YELLOW}📊 Environment Information:{RESET}")
    print(f"Local Python:      {local_report.get('python_version', 'Unknown')}")
    print(f"Production Python: {prod_report.get('python_version', 'Unknown')}")
    print(f"Local Report:      {local_file}")
    print(f"Production Report: {prod_file}")
    
    # Python version warning
    if local_report.get('python_version') != prod_report.get('python_version'):
        print(f"\n{YELLOW}⚠️  Warning: Python versions differ between environments!{RESET}")
    
    # Compare each category
    categories = ['core', 'critical', 'ai', 'optional']
    total_differences = 0
    
    for category in categories:
        local_data = local_report.get('checks', {}).get(category, {})
        prod_data = prod_report.get('checks', {}).get(category, {})
        
        local_packages = local_data.get('packages', [])
        prod_packages = prod_data.get('packages', [])
        
        differences = compare_packages(local_packages, prod_packages)
        
        if differences:
            total_differences += len(differences)
            print(f"\n{YELLOW}{local_data.get('category', category.title())} Differences:{RESET}")
            print(tabulate(differences, 
                         headers=["Package", "Local Version", "Production Version", "Status"],
                         tablefmt="grid"))
    
    # Missing packages summary
    print(f"\n{YELLOW}📦 Missing Packages Summary:{RESET}")
    
    for category in categories:
        local_data = local_report.get('checks', {}).get(category, {})
        prod_data = prod_report.get('checks', {}).get(category, {})
        
        local_missing = local_data.get('missing', [])
        prod_missing = prod_data.get('missing', [])
        
        if local_missing:
            print(f"\n{RED}Missing locally ({local_data.get('category', category)}):{RESET}")
            for pkg in local_missing:
                print(f"  - {pkg}")
        
        if prod_missing:
            print(f"\n{RED}Missing in production ({prod_data.get('category', category)}):{RESET}")
            for pkg in prod_missing:
                print(f"  - {pkg}")
    
    # Summary
    print(f"\n{YELLOW}📊 Summary:{RESET}")
    print("=" * 70)
    
    if total_differences == 0:
        print(f"{GREEN}✅ Environments are synchronized! No package differences found.{RESET}")
    else:
        print(f"{YELLOW}⚠️  Found {total_differences} package differences between environments.{RESET}")
        
        print(f"\n{YELLOW}Recommended actions:{RESET}")
        print("1. Review the differences above")
        print("2. Update requirements.txt if needed")
        print("3. Run on production:")
        print(f"   {CYAN}cd /opt/kuwait-social-ai/backend && pip install -r requirements.txt{RESET}")
        print("4. Restart the service:")
        print(f"   {CYAN}systemctl restart kuwait-backend{RESET}")
    
    # Save comparison
    comparison_file = f"environment_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(comparison_file, 'w') as f:
        f.write(f"Environment Comparison Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Total differences: {total_differences}\n")
        f.write(f"Local Python: {local_report.get('python_version')}\n")
        f.write(f"Production Python: {prod_report.get('python_version')}\n")
    
    print(f"\n📄 Comparison saved to: {comparison_file}")

if __name__ == "__main__":
    main()