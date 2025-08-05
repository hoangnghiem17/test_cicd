import requests
import time


def fetch_greeting():
    response = requests.get('https://api.github.com')
    if response.status_code == 200:
        return 'Hello, CI/CD Pipeline!'
    return 'Failed to fetch greeting'


if __name__ == "__main__":
    while True:
        print(fetch_greeting())
        time.sleep(60)  # Wait for 60 seconds before repeating 