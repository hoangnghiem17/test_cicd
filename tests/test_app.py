from app import fetch_greeting

def test_fetch_greeting():
    assert fetch_greeting() == 'Hello, CI/CD Pipeline!' 