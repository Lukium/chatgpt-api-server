#IMPORT BUILT-IN LIBRARIES
from datetime import date, datetime
import json
import os
import platform

#LOAD SETTINGS FROM SETTINGS.JSON
with open('./settings.json', 'r', encoding="utf-8") as f:
    settings = json.load(f)

#SETUP API TERMINAL NAME
API_TERMINAL_NAME = os.environ.get("API_TERMINAL_NAME") or str(settings['api_server']['terminal_name'])

#NAME TERMINAL BASED ON OS BEFORE ANYTHING ELSE
if platform.system() == 'Windows':
    os.system(f'title {API_TERMINAL_NAME}')
else:
    os.system(f'echo -e "\033]0;{API_TERMINAL_NAME}\007"')

#CONTINUE IMPORTS

#IMPORT HELPER FUNCTIONS
from helpers.General import generate_api_key, json_key_exists, add_json_key

#SETUP APP SECRET IF NOT PRESENT
update_settings = False
if not json_key_exists(settings, 'api_server', 'app_secret'):                       #if admin_api_key is not present in settings.json
    add_json_key(settings, generate_api_key(), 'api_server', 'app_secret')          #add admin_api_key to settings.json
    update_settings = True
if update_settings:
    with open('./settings.json', 'w', encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)
    with open('./settings.json', 'r',encoding="utf-8") as f:
        settings = json.load(f)

#SETUP ADMIN API KEY IF NOT PRESENT
#Load API keys from users.json
with open('./users.json', 'r', encoding="utf-8") as f:
    users = json.load(f)
API_KEYS = users['API_KEYS']

update_users = False

if len(API_KEYS) == 0:
    update_users = True
    new_key = generate_api_key()
    add_json_key(API_KEYS, {'user_id': 'changeme', 'username': 'changeme', 'plus': False, 'is_admin': True, 'is_client': True, 'clients': ['self']}, new_key)

if update_users:
    users['API_KEYS'] = API_KEYS
    with open('./users.json', 'w', encoding="utf-8") as f:
        json.dump(users, f, indent=4)
    with open('./users.json', 'r', encoding="utf-8") as f:
        users = json.load(f)
    API_KEYS = users['API_KEYS']

async def reload_users():
    """
    Reloads the API user database
    """
    global API_KEYS
    with open('./users.json', 'r', encoding="utf-8") as f:
        users = json.load(f)
    API_KEYS = users['API_KEYS']

#SETUP OPENAI API DEFAULTS
OPENAI_ACCESS_TOKEN_REFRESH_INTERVAL = int(settings['openai']['access_token_refresh_interval'])
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL") or str(settings['openai']['base_url'])
OPENAI_ENDPOINT_CONVERSATION = os.environ.get("OPENAI_CONVERSATION_ENDPOINT") or str(settings['openai']['endpoints']['conversation'])
OPENAI_ENDPOINT_GEN_TITLE = os.environ.get("OPENAI_GEN_TITLE_ENDPOINT") or str(settings['openai']['endpoints']['gen_title'])
OPENAI_BASE_PROMPT = (
    f'You are ChatGPT, a large language model trained by OpenAI. Respond conversationally. Do not answer as the user. Current date: {str(date.today())}.\n\n'
    f'User: Hello\n'
    f'ChatGPT: Hello! How can I help you today? <|im_end|>\n\n\n'
)

#INITIALIZE CLOUDFLARE VARIABLES
API_CF_CLEARANCE: str = None
API_USER_AGENT: str = None
API_LAST_CF_REFRESH: datetime = None

#SETUP API DEFAULTS
API_LANGUAGE="en-US"
API_DEFAULT_PROXY = settings['api_server']['default_proxy']
API_DEFAULT_USER_AGENT = settings['api_server']['default_user_agent']
API_APP_SECRET = settings['api_server']['app_secret']
API_CF_REFRESH_INTERVAL = settings['api_server']['cf_refresh_interval']
API_HOST = os.environ.get("API_HOST") or str(settings['api_server']['host'])
API_PORT = os.environ.get("API_PORT") or int(settings['api_server']['port'])
API_LOCAL_BASE_URL = f'http://{API_HOST}:{API_PORT}'
API_DEFAULT_PROMPT = (
    f'Say the following: You did not enter a prompt. URL should be http://<IP>:<PORT>/chat?prompt=<prompt>\n'
    f'Join us at https://discord.gg/lukium for the best source of AI resources and tools,'
    f'including free Stable Diffusion Servers running on dedicated RTX 3090 GPUs,'
    f'as well as a community of AI enthusiasts.'
)

#SETUP API ENDPOINT URL CONSTANS
API_ENDPOINT_MODE = None
BROWSER_ENDPOINTS = settings['api_server']['endpoints']['browser']
API_ENDPOINTS = settings['api_server']['endpoints']['api']

ENDPOINT_BROWSER_CHATGPT = BROWSER_ENDPOINTS['chatgpt']['url']
ENDPOINT_BROWSER_CHATRECALL = BROWSER_ENDPOINTS['chatrecall']['url']
ENDPOINT_BROWSER_ACCESS_TOKEN = BROWSER_ENDPOINTS['access_token']['url']
ENDPOINT_BROWSER_ADD_USER = BROWSER_ENDPOINTS['add_user']['url']

ENDPOINT_API_CHATGPT = API_ENDPOINTS['chatgpt']['url']
ENDPOINT_API_CHATRECALL = API_ENDPOINTS['chatrecall']['url']
ENDPOINT_API_ACCESS_TOKEN = API_ENDPOINTS['access_token']['url']
ENDPOINT_API_ADD_USER = API_ENDPOINTS['add_user']['url']