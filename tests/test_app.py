from app import fetch_greeting
 
def test_fetch_greeting():
    # Test default behavior (original test)
    assert fetch_greeting() == 'Hello, CI/CD Pipeline!' 
    
def test_fetch_greeting_with_custom_url():
    # Test with specific URL
    assert fetch_greeting('https://api.github.com') == 'Hello, CI/CD Pipeline!' 