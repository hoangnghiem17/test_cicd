import requests
import time


def fetch_greeting(url='https://api.github.com'):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return 'Hello, CI/CD Pipeline!'
        return 'Failed to fetch greeting'
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return 'Failed to fetch greeting'


if __name__ == "__main__":
    while True:
        print(fetch_greeting())
        time.sleep(60)  # Wait for 60 seconds before repeating