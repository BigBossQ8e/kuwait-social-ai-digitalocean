#!/bin/bash

echo "=== Debugging MAX_CONTENT_LENGTH Issue ==="
echo ""

echo "1. Checking MAX_CONTENT_LENGTH in app_factory.py:"
grep -n "MAX_CONTENT_LENGTH" app_factory.py || echo "Not found with uppercase"
grep -n "max_content_length" app_factory.py || echo "Not found with lowercase"
grep -n "app.config\['MAX" app_factory.py || echo "Not found in app.config"
echo ""

echo "2. Checking MAX_CONTENT_LENGTH in config/config.py:"
grep -n "MAX_CONTENT_LENGTH" config/config.py || echo "Not found in config.py"
echo ""

echo "3. Checking how it's loaded from environment:"
grep -A2 -B2 "getenv.*MAX_CONTENT" config/config.py || echo "Not found getenv pattern"
echo ""

echo "4. Current environment value:"
python3 -c "import os; print(f'MAX_CONTENT_LENGTH from env: {os.getenv(\"MAX_CONTENT_LENGTH\")} (type: {type(os.getenv(\"MAX_CONTENT_LENGTH\"))})')"
echo ""

echo "5. Checking if environment variable is set:"
echo "MAX_CONTENT_LENGTH env var: $MAX_CONTENT_LENGTH"
echo ""

echo "6. Looking for any file size/content length related configs:"
grep -r "MAX_CONTENT\|max_content\|FILE_SIZE\|file_size" config/ --include="*.py" | head -20
echo ""

echo "7. Checking Flask app configuration loading:"
grep -A5 -B5 "from_object\|from_envvar\|update" app_factory.py | grep -v "^--$"
echo ""

echo "8. Checking for any integer conversion of MAX_CONTENT_LENGTH:"
grep -r "int.*MAX_CONTENT\|MAX_CONTENT.*int" . --include="*.py" | head -10
echo ""

echo "9. Looking for the actual error location:"
echo "Searching for comparisons with MAX_CONTENT_LENGTH..."
grep -r "MAX_CONTENT.*>\|<.*MAX_CONTENT" . --include="*.py" | head -10