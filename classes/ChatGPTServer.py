#IMPORT BUILT-IN LIBRARIES
import asyncio
import json

#IMPORT THIRD-PARTY LIBRARIES
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension

#IMPORT CONTRIBUTED-CODE LIBRARIES
from contrib.OpenAIAuth.OpenAIAuth import OpenAIAuth

#IMPORT CLASSES
from classes.ChatGPT import ChatGPT

import settings.Settings as Settings

from htmls.Blocks import *

class ChatGPTServer:
    def __init__(self, **kwargs) -> None:
        self.current_chatgpt_any = 0
        self.current_chatgpt_free = 0
        self.current_chatgpt_plus = 0
        self.chatgpt_instances: list = []
        self.chatgpt_free_instances: list = []
        self.chatgpt_plus_instances: list = []        
        with open('./settings.json', 'r') as f:
            self.settings = json.load(f)

    @classmethod
    async def create(cls, **kwargs):
        current_chatgpt_any = 0
        current_chatgpt_free = 0
        current_chatgpt_plus = 0
        with open('./settings.json', 'r') as f:
            settings = json.load(f)
        self = cls(current_chatgpt_any=current_chatgpt_any, current_chatgpt_free=current_chatgpt_free, current_chatgpt_plus=current_chatgpt_plus, settings=settings)
        await self.__load_chatgpt_instances()
        return self


    #SETUP CHATGPT INSTANCES
    async def __load_chatgpt_instances(self) -> list:
        openai_instances = self.settings['openai']['instances']
        #cf_clearance, user_agent = await first_cloudflare()
        self.chatgpt_instances = [await ChatGPT.create(instance=openai_instances.index(instance), cf_clearance=Settings.API_CF_CLEARANCE, user_agent=Settings.API_USER_AGENT) for instance in openai_instances]
        if len(self.chatgpt_instances) == 0:
            raise Exception('No OpenAI instances were found in settings.json')
        self.chatgpt_free_instances = [instance for instance in self.chatgpt_instances if instance.plus == False]
        self.chatgpt_plus_instances = [instance for instance in self.chatgpt_instances if instance.plus == True]
        print(f'ChatGPT Free Instances Loaded: {len(self.chatgpt_free_instances)}')
        print(f'ChatGPT Plus Instances Loaded: {len(self.chatgpt_plus_instances)}')

    #SETUP HELPER FUNCTIONS
    async def __get_chatgpt(self, **kwargs):
        type: str = kwargs.get('type', None)
        if type == 'any':
            chatgpt = self.chatgpt_instances[self.current_chatgpt_any]
            self.current_chatgpt_any += 1
            if self.current_chatgpt_any >= len(self.chatgpt_instances):
                self.current_chatgpt_any = 0
        elif type == 'free':
            chatgpt = self.chatgpt_free_instances[self.current_chatgpt_free]
            self.current_chatgpt_free += 1
            if self.current_chatgpt_free >= len(self.chatgpt_free_instances):
                self.current_chatgpt_free = 0
        elif type == 'plus':
            chatgpt = self.chatgpt_plus_instances[self.current_chatgpt_plus]
            self.current_chatgpt_plus += 1
            if self.current_chatgpt_plus >= len(self.chatgpt_plus_instances):
                self.current_chatgpt_plus = 0
        return chatgpt

    """
    async def get_chatgpt_free(chatgpt_instances: list):    
        global current_chatgpt_free
        chatgpt = chatgpt_instances[current_chatgpt_free]
        current_chatgpt_free += 1
        if current_chatgpt_free >= len(chatgpt_instances):
            current_chatgpt_free = 0
        return chatgpt

    async def get_chatgpt_plus(chatgpt_instances: list):    
        global current_chatgpt_plus
        chatgpt = chatgpt_instances[current_chatgpt_plus]
        current_chatgpt_plus += 1
        if current_chatgpt_plus >= len(chatgpt_instances):
            current_chatgpt_plus = 0
        return chatgpt
    """
    
    async def chatgpt_instances_cloudflare_refresh():
        Settings.refresh_cloudflare()
        for instance in Settings.chatgpt_instances:
            instance.cf_clearance = Settings.API_CF_CLEARANCE
            instance.user_agent = Settings.API_USER_AGENT
        for instance in Settings.chatgpt_free_instances:
            instance.cf_clearance = Settings.API_CF_CLEARANCE
            instance.user_agent = Settings.API_USER_AGENT
        for instance in Settings.chatgpt_plus_instances:
            instance.cf_clearance = Settings.API_CF_CLEARANCE
            instance.user_agent = Settings.API_USER_AGENT
        return

    async def check_user(self, **kwargs) -> dict:
        user = kwargs.get('user', None)
        API_KEYS = Settings.API_KEYS
        response: dict = {}

        if user is None:
            response['status'] = 'error'
            response['message'] = 'No user specified'
            return response
        elif user not in API_KEYS:
            response['status'] = 'error'
            response['message'] = 'Invalid user specified'
            return response
        else:
            response['status'] = 'success'
            response['message'] = 'User is valid'
        
        #print(response)
        return response

    async def retrieve_access_token(self, **kwargs) -> str:
        email = kwargs.get('email', None)
        password = kwargs.get('password', None)
        auth = OpenAIAuth(
                email_address=email,
                password=password,            
                proxy=Settings.API_DEFAULT_PROXY
            )        
        await auth.begin()
        access_token = await auth.get_access_token()

        return access_token

    async def process_chagpt_request(self, **kwargs) -> dict:
        prompt: str = kwargs.get('prompt', Settings.API_DEFAULT_PROMPT)
        plus: str = kwargs.get('plus', 'any')
        type: str = kwargs.get('type', 'builtin')
        access_token: str = kwargs.get('access_token', None)
        user_plus: str = kwargs.get('user_plus', 'false')
        #API_KEYS = Settings.API_KEYS
        response: dict = {}

        if type == 'user':
            chatgpt = await ChatGPT.create(instance=0,
                                            cf_clearance=Settings.API_CF_CLEARANCE,
                                            user_agent=Settings.API_USER_AGENT,
                                            type='user',
                                            user_access_token=access_token,
                                            user_plus=user_plus
                                                )
            print(f'ChatGPT Instance: {chatgpt.instance}')
            print(f'ChatGPT Access Token: {chatgpt.access_token}')
            print(f'ChatGPT cf clearance {chatgpt.cf_clearance}')
            print(f'ChatGPT User Agent: {chatgpt.user_agent}')
            print(f'ChatGPT Plus: {chatgpt.plus}')

        elif type == 'builtin':
            if plus == "any":
                chatgpt: ChatGPT = await self.__get_chatgpt(type='any')
            elif plus == "false":
                chatgpt: ChatGPT = await self.__get_chatgpt(type='free')                
            elif plus == "true":
                chatgpt: ChatGPT = await self.__get_chatgpt(type='plus')
            print(f'Using ChatGPT Instance: {chatgpt.email}')
            print(f'ChatGPT Plus? {chatgpt.plus}')

        response = await chatgpt.ask(prompt)

        return response

    async def process_reply_only(self, **kwargs) -> str:
        response: dict = kwargs.get('response', None)
        pretty: str = kwargs.get('pretty', 'false')
        reply_only_response = response['message']['content']['parts'][0]
        if pretty == "true":
            md = markdown.Markdown(extensions=['fenced_code', 'nl2br', CodeHiliteExtension(linenums=True, guess_lang=True, use_pygmnet=True, css_class='highlight')])
            reply_only_response = md.convert(reply_only_response)
            reply_only_response = HTML_HEADER + reply_only_response + HTML_FOOTER
            return reply_only_response
        else:
            return reply_only_response