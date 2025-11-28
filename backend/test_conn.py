import requests
import sys

try:
    print("Testing connection to http://alphaforge-backend:5000/health...")
    resp = requests.get('http://alphaforge-backend:5000/health', timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
