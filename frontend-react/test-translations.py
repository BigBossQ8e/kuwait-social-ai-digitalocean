import requests
import json

# Test the translations endpoint
response = requests.get('http://localhost:5000/api/translations')
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Test with specific locale
response_en = requests.get('http://localhost:5000/api/translations?locale=en')
print(f"\nEnglish Status: {response_en.status_code}")
print(f"English Response: {response_en.text[:200]}")
EOF < /dev/null
