import requests

def fetch_greeting():
    response = requests.get('https://api.github.com')
    if response.status_code == 200:
        return 'Hello, CI/CD Pipeline!'
    return 'Failed to fetch greeting' 