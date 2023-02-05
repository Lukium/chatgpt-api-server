#IMPORT BUILT-IN LIBRARIES
import json
import os
from datetime import date

#IMPORT THIRD-PARTY LIBRARIES
import openai
import tiktoken

#LOAD JSON SETTINGS FROM config.json
with open('./config.json', 'r') as f:
    data = json.load(f)

#API ENDPOINT SETTINGS
API_HOST = os.environ.get("API_HOST") or data['api_endpoint_host']
API_PORT = int(os.environ.get("API_PORT") or data['api_endpoint_port'])

#OPENAI SETTINGS
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or data['openai_api_key']
OPENAI_MODEL = os.environ.get("OPENAI_MODEL") or data['opeai_model']
OPENAI_DEFAULT_TEMPERATURE = os.environ.get("OPENAI_TEMPERATURE") or float(data['openai_default_temperature'])
OPENAI_MAX_TOKENS = int(data['openai_max_tokens'])
if "openai_custom_base_prompt" in data:
    OPENAI_CUSTOM_BASE_PROMPT = data['openai_custom_base_prompt']
else:
    OPENAI_CUSTOM_BASE_PROMPT = (
        f'You are ChatGPT, a large language model trained by OpenAI. Respond conversationally. Do not answer as the user. Current date: {str(date.today())}.\n\n'
        f'User: Hello\n'
        f'ChatGPT: Hello! How can I help you today? <|im_end|>\n\n\n'
    )

#DEFINE OTHER SETTINGS
openai.api_key = OPENAI_API_KEY
ENCODER = tiktoken.get_encoding("gpt2")

OPENAI_DEFAULT_PROMPT = (
    f'''Say the following: You did not enter a prompt. URL should be http://<IP>:<PORT>/chat?prompt=<prompt>

    Join us at https://discord.gg/lukium for the best source of AI resources and tools,
    including free Stable Diffusion Servers running on dedicated RTX 3090 GPUs,
    as well as a community of AI enthusiasts.'''
)

#DEFINE SETTINGS FUNCTIONS
async def get_max_tokens(prompt: str) -> int:
    """
    Return the maximum number of tokens that can be used in a request based on the prompt length by using the OpenAI API's encoder as well as the openai_max_tokens in config.json.
    """
    return OPENAI_MAX_TOKENS - len(ENCODER.encode(prompt))