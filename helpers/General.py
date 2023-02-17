#IMPORT BUILT-IN LIBRARIES
import re
import secrets
import string

def is_valid_socks5_url(url: str) -> bool:
    """
    Validates if a string is a valid Socks5 URL.
    
    Args:
    url (str): The URL to validate.
    
    Returns:
    bool: True if the URL is a valid Socks5 URL, False otherwise.
    """
    
    # Socks5 URL regex pattern
    pattern = r'^socks5://(\d{1,3}\.){3}\d{1,3}:\d{1,5}$'
    
    # Check if the URL matches the pattern
    if re.match(pattern, url):
        return True
    
    return False

def generate_api_key(length=32) -> str:
    """
    Generates a random API key
    """
    chars = string.ascii_letters + string.digits
    while True:
        api_key = ''.join(secrets.choice(chars) for _ in range(length))
        if (any (c.islower() for c in api_key)
            and any (c.isupper() for c in api_key)
            and sum (c.isdigit() for c in api_key) >= 3):
            break
    return api_key

def json_key_exists(data, *keys):
    """
    Checks if a key exists in a JSON dictionary
    """
    if isinstance(data, dict):
        if keys[0] in data.keys():
            if len(keys) > 1:
                return json_key_exists(data[keys[0]], *keys[1:])
            else:
                return True
        else:
            return False
    else:
        return False

def json_value_exists(data, value):
    if isinstance(data, dict):
        for val in data.values():
            if json_value_exists(val, value):
                return True
    elif data == value:
        return True
    return False

def add_json_key(data, value, *keys):
    """
    Adds a key to a JSON dictionary
    """
    if len(keys) == 1:
        data[keys[0]] = value
    else:
        if keys[0] not in data.keys():
            data[keys[0]] = {}
        add_json_key(data[keys[0]], value, *keys[1:])