#!/usr/bin/env python3
"""
Verify that requirements.txt matches installed packages
Helps identify version mismatches and missing packages
"""

import subprocess
import sys
import re
from packaging import version
from packaging.requirements import Requirement
import importlib.metadata

def parse_requirements(filename):
    """Parse requirements.txt file"""
    requirements = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#') or line.startswith('-'):
                    continue
                
                try:
                    req = Requirement(line)
                    requirements[req.name.lower()] = req
                except:
                    # Handle special cases like URLs or editable installs
                    pass
    except FileNotFoundError:
        print(f"❌ {filename} not found")
        return {}
    
    return requirements

def get_installed_packages():
    """Get all installed packages"""
    installed = {}
    try:
        import pkg_resources
        for dist in pkg_resources.working_set:
            installed[dist.project_name.lower()] = dist.version
    except:
        # Fallback to pip list
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            import json
            packages = json.loads(result.stdout)
            for pkg in packages:
                installed[pkg['name'].lower()] = pkg['version']
    
    return installed

def check_requirement(req, installed_version):
    """Check if installed version satisfies requirement"""
    if not installed_version:
        return False, "Not installed"
    
    try:
        installed_ver = version.parse(installed_version)
        if req.specifier.contains(installed_ver):
            return True, f"✅ {installed_version}"
        else:
            return False, f"❌ {installed_version} (need {req.specifier})"
    except:
        return True, f"⚠️  {installed_version} (can't verify)"

def main():
    print("\n🔍 Requirements Verification")
    print("=" * 60)
    
    # Check for requirements files
    req_files = ['requirements.txt', 'requirements.in', 'requirements-prod.txt']
    
    for req_file in req_files:
        print(f"\n📄 Checking {req_file}...")
        print("-" * 60)
        
        requirements = parse_requirements(req_file)
        if not requirements:
            continue
        
        installed = get_installed_packages()
        
        missing = []
        mismatched = []
        satisfied = []
        
        for name, req in sorted(requirements.items()):
            installed_version = installed.get(name)
            ok, status = check_requirement(req, installed_version)
            
            if not installed_version:
                missing.append(f"  {req.name}")
            elif not ok:
                mismatched.append(f"  {req.name}: {status}")
            else:
                satisfied.append(f"  {req.name}: {status}")
        
        # Print results
        if satisfied:
            print(f"\n✅ Satisfied ({len(satisfied)}):")
            if len(satisfied) <= 10:
                for item in satisfied:
                    print(item)
            else:
                print(f"  {len(satisfied)} packages are correctly installed")
        
        if mismatched:
            print(f"\n⚠️  Version Mismatches ({len(mismatched)}):")
            for item in mismatched:
                print(item)
        
        if missing:
            print(f"\n❌ Missing ({len(missing)}):")
            for item in missing:
                print(item)
        
        # Summary for this file
        total = len(requirements)
        ok_count = len(satisfied)
        print(f"\n📊 Summary: {ok_count}/{total} requirements satisfied")
    
    # Check for packages not in requirements
    print("\n🔍 Checking for extra packages...")
    print("-" * 60)
    
    if 'requirements.txt' in req_files:
        requirements = parse_requirements('requirements.txt')
        installed = get_installed_packages()
        
        req_names = {name.lower() for name in requirements.keys()}
        installed_names = set(installed.keys())
        
        extra = installed_names - req_names
        # Filter out common build tools and standard library packages
        exclude_patterns = ['pip', 'setuptools', 'wheel', 'pkg-resources', 'pkginfo', 
                          'importlib-', 'typing-', 'backports']
        
        extra_filtered = []
        for pkg in sorted(extra):
            if not any(pattern in pkg for pattern in exclude_patterns):
                extra_filtered.append(f"  {pkg}: {installed[pkg]}")
        
        if extra_filtered:
            print(f"\n📦 Packages installed but not in requirements.txt ({len(extra_filtered)}):")
            if len(extra_filtered) <= 20:
                for item in extra_filtered:
                    print(item)
            else:
                print(f"  {len(extra_filtered)} extra packages found")
    
    # Provide actionable recommendations
    print("\n💡 Recommendations:")
    print("=" * 60)
    
    if missing:
        print(f"1. Install missing packages:")
        print(f"   pip install -r requirements.txt")
    
    if mismatched:
        print(f"2. Fix version mismatches:")
        print(f"   pip install --upgrade -r requirements.txt")
    
    if extra_filtered and len(extra_filtered) > 10:
        print(f"3. Consider cleaning up extra packages:")
        print(f"   pip freeze > current.txt")
        print(f"   # Review and clean up current.txt")
    
    print("\n✅ Verification complete!")

if __name__ == "__main__":
    main()