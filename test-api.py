import requests
import json

url = "https://kwtsocial.com/api/auth/login"
data = {
    "email": "test@kwtsocial.com",
    "password": "Admin123\!"
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print(f"Headers: {response.headers}")
