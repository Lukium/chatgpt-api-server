#IMPORT BUILT-IN LIBRARIES
import json

#IMPORT HELPER FUNCTIONS
from helpers.General import generate_api_key, json_key_exists, json_value_exists, add_json_key #For adding API keys to users.json

import settings.Settings as settings

def reload_users():
    """
    Reloads the API user database
    """
    with open('./users.json', 'r') as f:
        keys = json.load(f)
    settings.API_KEYS = keys['API_KEYS']

def add(**kwargs):
    """
    Adds a user to the user database
    """
    userid: str = str(kwargs['userid'])
    username: str = str(kwargs['username'])
    plus: bool = kwargs['plus']

    if json_value_exists(settings.API_KEYS, userid):
        status = 'error'
        message = 'User already exists'
        key = None
        return status, message, key
    else:
        api_key = generate_api_key()
        add_json_key(settings.API_KEYS, {
            'user_id': userid,
            'username': username,
            'plus': plus,
        }, api_key)
        with open('./users.json', 'r') as f:
            keys = json.load(f)
        keys['API_KEYS'] = settings.API_KEYS
        with open('./users.json', 'w') as f:
            json.dump(keys, f, indent=4)
        reload_users()
        if json_value_exists(settings.API_KEYS, userid):
            status = 'success'
            message = 'User added'
            key = api_key
            return status, message, key
        else:
            status = 'error'
            message = 'User not added'
            key = None
            return status, message, key