#IMPORT BUILT-IN LIBRARIES
from copy import deepcopy
from datetime import datetime
import json

#IMPORT THIRD-PARTY LIBRARIES
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension

#IMPORT CONTRIBUTED-CODE LIBRARIES
from contrib.OpenAIAuth.OpenAIAuth import OpenAIAuth
from contrib.OpenAIAuth.Cloudflare import Cloudflare

#IMPORT CLASSES
from classes.ChatGPT import ChatGPT
from classes.ChatGPTClient import ChatGPTClient

#IMPORT HELPER FUNCTIONS
from helpers.General import generate_api_key, json_value_exists, add_json_key

import settings.Settings as Settings

from htmls.Blocks import *

class ChatGPTServer:
    def __init__(self, **kwargs) -> None:
        self.current_chatgpt_any = 0
        self.current_chatgpt_free = 0
        self.current_chatgpt_plus = 0
        self.users: dict = {}
        self.conversations: dict = {}
        self.chatgpt_instances: list = []
        self.chatgpt_free_instances: list = []
        self.chatgpt_plus_instances: list = []
        self.clients: list = []
        with open('./settings.json', 'r', encoding="utf-8") as f:
            self.settings = json.load(f)

    @classmethod
    async def create(cls, **kwargs) -> 'ChatGPTServer':
        """
        Creates a new instance of the ChatGPTServer class asynchronously and returns it
        """        
        current_chatgpt_any = 0
        current_chatgpt_free = 0
        current_chatgpt_plus = 0
        with open('./settings.json', 'r', encoding="utf-8") as f:
            settings = json.load(f)
        self = cls(current_chatgpt_any=current_chatgpt_any, current_chatgpt_free=current_chatgpt_free, current_chatgpt_plus=current_chatgpt_plus, settings=settings)
        await self.__load_chatgpt_instances()
        await self.__refresh_cloudflare()
        await self.__load_api_users()
        await self.__load_client_users()
        await self.__load_conversations()
        return self

    #SETUP CHATGPT INSTANCES
    async def __load_chatgpt_instances(self) -> None:
        """
        Loads all ChatGPT instances from settings.json
        """
        openai_instances = self.settings['openai']['instances']
        self.chatgpt_instances = [await ChatGPT.create(instance=openai_instances.index(instance)) for instance in openai_instances]
        if len(self.chatgpt_instances) == 0:
            raise Exception('No OpenAI instances were found in settings.json')
        self.chatgpt_free_instances = [instance for instance in self.chatgpt_instances if instance.plus == False]
        self.chatgpt_plus_instances = [instance for instance in self.chatgpt_instances if instance.plus == True]
        print(f'ChatGPT Free Instances Loaded: {len(self.chatgpt_free_instances)}')
        print(f'ChatGPT Plus Instances Loaded: {len(self.chatgpt_plus_instances)}')
        Settings.API_ENDPOINT_MODE = 'bp'
    
    async def __load_api_users(self) -> dict:
        """
        Loads all API users from users.json
        """
        with open('./users.json', 'r', encoding="utf-8") as f:
            users = (json.load(f))['API_KEYS']
        self.users = users
        Settings.API_KEYS = users
        
    async def __reload_client_users(self, **kwargs) -> None:
        """
        Reloads users belonging to a client
        """
        client_id_to_reload = kwargs.get('client_id_to_reload', None)
        
        client_instance: ChatGPTClient = [server_client for server_client in self.clients if server_client.identity == client_id_to_reload][0]
        
        for user, user_data in self.users.items():
            for client in user_data['clients']:
                if client == client_id_to_reload:
                    if user not in client_instance.users:
                        client_instance.users[user] = user_data
                        client_instance.user_ids.append(user_data['user_id'])
    
    async def __load_client_users(self):
        """
        Loads all client users from users.json
        """
        clients_to_add = set()
        
        client_users_dict = {}
        for user, user_data in self.users.items():
            for client in user_data['clients']:
                if client != 'self':
                    if client not in client_users_dict:
                        client_users_dict[client] = []
                    client_users_dict[client].append(user)
        
        clients_to_add = [(client, users) for client, users in client_users_dict.items() if len(users) > 0]
        
        for user, user_data in self.users.items():
            add_client = True
            if 'is_client' in user_data:
                if user_data['is_client'] == True:
                    for client in clients_to_add:
                        if client[0] == user_data['user_id']:
                            add_client = False
                            break
                    if add_client == True:
                        clients_to_add.append((user_data['user_id'], []))
        
        for client, client_users in clients_to_add:
            self.clients.append(await ChatGPTClient.create(client_id=client, client_users=client_users, server_users=self.users))
            print(f'Client {client} loaded with {len(client_users)} {len(client_users) == 1 and "user" or "users"}')
    
    async def __load_conversations(self) -> dict:
        """
        Loads all conversations from conversations.json
        """
        with open('./conversations.json', 'r', encoding="utf-8") as f:
            conversations = (json.load(f))
        self.conversations = conversations
    
    async def __refresh_cloudflare(self) -> None:
        """
        Refreshes the Cloudflare Clearance and User Agent
        """        
        if Settings.API_ENDPOINT_MODE == None:
            current_time = datetime.now()
            if Settings.API_LAST_CF_REFRESH is not None:
                time_delta = (current_time - Settings.API_LAST_CF_REFRESH).total_seconds()
                if time_delta > Settings.API_CF_REFRESH_INTERVAL:
                    refresh = True
                else:
                    refresh = False
            else:
                refresh = True
            if refresh:
                print(f'Starting Cloudflare Refresh')
                print(f'Current Cloudflare Clearance: {Settings.API_CF_CLEARANCE}')
                print(f'Current User Agent: {Settings.API_USER_AGENT}')            
                Settings.API_CF_CLEARANCE, Settings.API_USER_AGENT = await Cloudflare(proxy=Settings.API_DEFAULT_PROXY).a_get_cf_cookies()
                Settings.API_LAST_CF_REFRESH = datetime.now()
                print(f'New Cloudflare Clearance: {Settings.API_CF_CLEARANCE}')
                print(f'New User Agent: {Settings.API_USER_AGENT}')
                if len(self.chatgpt_instances) > 0:
                    for instance in self.chatgpt_instances:
                        instance.cf_clearance = Settings.API_CF_CLEARANCE
                        instance.user_agent = Settings.API_USER_AGENT
                if len(self.chatgpt_free_instances) > 0:
                    for instance in self.chatgpt_free_instances:
                        instance.cf_clearance = Settings.API_CF_CLEARANCE
                        instance.user_agent = Settings.API_USER_AGENT
                if len(self.chatgpt_plus_instances) > 0:
                    for instance in self.chatgpt_plus_instances:
                        instance.cf_clearance = Settings.API_CF_CLEARANCE
                        instance.user_agent = Settings.API_USER_AGENT
            else:
                print(f'Cloudflare Refresh Not Needed - Last Refresh: {Settings.API_LAST_CF_REFRESH} - Time Delta: {time_delta} - Interval: {Settings.API_CF_REFRESH_INTERVAL}')
        else:
            Settings.OPENAI_BASE_URL = Settings.OPENAI_BASE_URL.replace('chat', 'apps').replace('backend-', '')

    #SETUP HELPER FUNCTIONS
    async def __get_chatgpt(self, **kwargs) -> ChatGPT:
        """
        Returns a ChatGPT instance based on the type of instance requested.
        """
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

    async def check_user(self, **kwargs) -> dict:
        """
        Check if a user is valid
        """
        user = kwargs.get('user', None)
        response: dict = {}

        if user is None:
            response['status'] = 'error'
            response['message'] = 'No user specified'
            return response
        elif user not in self.users:
            response['status'] = 'error'
            response['message'] = 'Invalid user specified'
            return response
        else:
            response['status'] = 'success'
            response['message'] = 'User is valid'
            
        return response
    
    async def check_admin(self, **kwargs) -> dict:
        """
        Check if admin is valid
        """
        await self.__load_api_users()
        user = kwargs.get('user', None)
        response: dict = {}

        if user is None:
            response['status'] = 'error'
            response['message'] = 'No user specified'
            return response
        elif user not in self.users:
            response['status'] = 'error'
            response['message'] = 'Invalid user specified'
            return response
        else:
            if 'is_admin' in self.users[user]:
                if self.users[user]['is_admin'] == True:
                    response['status'] = 'success'
                    response['message'] = 'Admin validated'
                else:
                    response['status'] = 'error'
                    response['message'] = 'Admin not validated'
            else:
                response['status'] = 'error'
                response['message'] = 'Admin not validated'

        return response
    
    async def check_client(self, **kwargs) -> dict:
        """
        Check if a client is valid
        """
        await self.__load_api_users()
        user = kwargs.get('user', None)
        response: dict = {}

        if user is None:
            response['status'] = 'error'
            response['message'] = 'No client specified'
            return response
        elif user not in self.users:
            response['status'] = 'error'
            response['message'] = 'Invalid client specified'
            return response
        else:
            if 'is_client' in self.users[user]:
                if self.users[user]['is_client'] == True:
                    response['status'] = 'success'
                    response['message'] = 'Client validated'
                else:
                    response['status'] = 'error'
                    response['message'] = 'Client not validated'
            else:
                response['status'] = 'error'
                response['message'] = 'Admin not validated'

        return response
    
    async def client_user_id_check(self, **kwargs) -> dict:
        """
        Check if a client user exists, if so return its API Key, otherwise create a new user and return its API Key
        """
        await self.__load_api_users()
        client = kwargs.get('client')
        user_id = kwargs.get('user_id')
        username = kwargs.get('username')
        user_id_plus = kwargs.get('user_id_plus')
        
        response: dict = {}
        
        client_id: str = self.users[client]['user_id']
        
        client_instance: ChatGPTClient = [server_client for server_client in self.clients if server_client.identity == client_id][0]
        
        if user_id not in client_instance.user_ids:
            status, message, key = await self.add_user(client = client, userid = user_id, username = username, plus = user_id_plus)
            response['status'] = status
            response['message'] = message
            response['key'] = key
            await self.__reload_client_users(client_id_to_reload=client_id)
        else:
            for key, value in client_instance.users.items():
                if value['user_id'] == user_id:
                    response['status'] = 'success'
                    response['message'] = 'User already exists'
                    response['key'] = key
                    break

        return response

    async def retrieve_access_token(self, **kwargs) -> str:
        """
        Retrieve an access token for a user
        """
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
    
    async def __spawn_user_chatgpt(self, **kwargs) -> ChatGPT:
        """
        Spawn a new ChatGPT instance for a user
        """
        user: str = kwargs.get('user', None)
        access_token: str = kwargs.get('access_token', None)
        user_plus: str = kwargs.get('user_plus', 'false')

        chatgpt = await ChatGPT.create(instance=0,
                                                cf_clearance=Settings.API_CF_CLEARANCE,
                                                user_agent=Settings.API_USER_AGENT,
                                                type='user',
                                                user_access_token=access_token,
                                                user_plus=user_plus,
                                                user=user
                                                    )
        return chatgpt
    
    async def __store_conversation(self, **kwargs) -> None:
        """
        Store conversation data in JSON file
        """
        client_id: str = kwargs.get("client_id")
        user: str = kwargs.get("user")
        response: dict = kwargs.get("response")
        user_id: str = Settings.API_KEYS[user]['user_id']
        conversation_id: str = response['conversation_id']
        message_id: str = response['message']['id']

        #Build conversation data
        data = {
            'prompt': response['api_prompt'],            
            'reply': response['message']['content']['parts'][0],
            'origin_time':  response['api_prompt_time_origin'],
        }

        conversations_users = deepcopy(self.conversations)
        api_users = self.users

        if user_id not in conversations_users['users']:
            add_json_key(conversations_users['users'], {'username': api_users[user]['username'], 'conversations': {}}, user_id)
        user_conversations = conversations_users['users'][user_id]['conversations']
            
        if conversation_id not in user_conversations:
            add_json_key(user_conversations, {'title': response['conversation_title'], 'api_instance_type': response['api_instance_type'], 'api_instance': response['api_instance_identity'], 'messages': {}}, conversation_id)
        conversation_messages = user_conversations[conversation_id]['messages']

        if message_id not in conversation_messages:
            add_json_key(conversation_messages, data, message_id)

        with open('conversations.json', 'w', encoding="utf-8") as f:
            json.dump(conversations_users, f, ensure_ascii=False, indent=4)
        
        await self.__load_conversations()
    
    async def __sort_conversation_chronologically(self, **kwargs) -> list:
        """
        Sort a dictionary by value of subkey
        """
        user_messages = kwargs.get('user_messages', None)
        for k, v in user_messages.items():
            v["origin_time"] = datetime.strptime(v["origin_time"], "%Y-%m-%d %H:%M:%S.%f")
        sorted_list = sorted(user_messages.items(), key=lambda x: x[1]["origin_time"])
        return sorted_list

    async def recall(self, **kwargs) -> dict:
        """
        Recalls a conversation from the conversation database
        """
        user: str = kwargs.get('user', None)
        conversation_id: str = kwargs.get('conversation_id', "")
        user_id = self.users[user]['user_id']

        #Create a copy of the conversation data using deepcopy to avoid modifying the original data
        user_conversations = deepcopy(self.conversations['users'][user_id]['conversations'])        
        
        response = {}
        if conversation_id == "":
            for key in user_conversations:
                response[key] = {
                    'title': user_conversations[key]['title'],
                }
        else:
            response['conversation_id'] = conversation_id
            response['conversation_title'] = user_conversations[conversation_id]['title']

            user_messages = user_conversations[conversation_id]['messages']
            sorted_messages = await self.__sort_conversation_chronologically(user_messages=user_messages)
            for message in sorted_messages:
                message[1].pop('origin_time')
            final_list: list = []
            for message in sorted_messages:
                message_dict = {
                    message[0] : message[1]
                }
                final_list.append(message_dict)
            response['messages'] = final_list
        
        return response

    async def process_chagpt_request(self, **kwargs) -> dict:
        """
        Process a ChatGPT request
        """
        if Settings.API_ENDPOINT_MODE == None:
            await self.__refresh_cloudflare()
        client: str = kwargs.get('client', 'self')
        user: str = kwargs.get('user', None)
        prompt: str = kwargs.get('prompt', Settings.API_DEFAULT_PROMPT)
        conversation_id: str = kwargs.get('conversation_id', '')
        plus: str = kwargs.get('plus', 'any')
        type: str = kwargs.get('type', 'builtin')
        access_token: str = kwargs.get('access_token', None)
        user_plus: str = kwargs.get('user_plus', 'false')

        chatgpt: ChatGPT = None #Initialize ChatGPT instance

        response: dict = {}
        followup: bool = False
        conversation_last_message_id: str = None
        
        if client == 'self' or client is None:
            client_id = 'self'
        else:            
            client_id = self.users[client]['user_id']
        
        user_id = self.users[user]['user_id']

        if conversation_id != "" and conversation_id is not None:
            followup = True
            conversation_users = self.conversations['users']
            
            #Check if user has conversations
            if user_id not in conversation_users:
                response['status'] = 'error'
                response['message'] = 'This user does not appear to have any conversations. Please start a new conversation using this user.'
                return response
            else:
                user_conversations = conversation_users[user_id]['conversations']
            
            #Check if conversation exists
            if conversation_id not in user_conversations:
                response['status'] = 'error'
                response['message'] = 'Conversation not found. It either does not exist or has been purged from the cache. Please try again with a new conversation id or start a new conversation.'
                return response
            else:
                conversation = user_conversations[conversation_id]
                conversation_title = conversation['title']
                api_instance_type = conversation['api_instance_type']

            #Check if conversation was started using the same API Instance type
            if type != api_instance_type:
                response['status'] = 'error'
                if type == 'builtin':
                    response['message'] = 'Conversation found, but was started using an Access Token. Please use the Access Token to continue the conversation.'
                elif type == 'user':
                    response['message'] = 'Conversation found, but was started using a Builtin API Instance. Please remove the Access Token to continue the conversation using Builtin API Instance.'
                return response
            
            user_messages = deepcopy(conversation['messages'])
            sorted_messages = await self.__sort_conversation_chronologically(user_messages=user_messages)
            conversation_last_message_id = sorted_messages[-1][0]
            last_message_prompt = sorted_messages[-1][1]['prompt']
            last_message_reply = sorted_messages[-1][1]['reply']
        
            if type == 'builtin':
                target_instance = conversation['api_instance']
                chatgpt: ChatGPT = next((x for x in self.chatgpt_instances if x.identity == target_instance), None)
                if chatgpt is None:
                    response['status'] = 'error'
                    response['message'] = 'Conversation found, but the previously used API Instance was not found. Please try again.'
                    return response
            elif type == 'user':
                chatgpt: ChatGPT = await self.__spawn_user_chatgpt(user=user, access_token=access_token, user_plus=user_plus)
                
        else:
            if type == 'user':
                chatgpt: ChatGPT = await self.__spawn_user_chatgpt(user=user, access_token=access_token, user_plus=user_plus)                

            elif type == 'builtin':
                if plus == "any":
                    chatgpt: ChatGPT = await self.__get_chatgpt(type='any')
                elif plus == "false":
                    chatgpt: ChatGPT = await self.__get_chatgpt(type='free')                
                elif plus == "true":
                    chatgpt: ChatGPT = await self.__get_chatgpt(type='plus')

        response: dict = await chatgpt.ask(user=user, prompt=prompt, conversation_id=conversation_id, parent_message_id=conversation_last_message_id)        

        if followup:
            response['conversation_title'] = conversation_title
            response['last_message_prompt'] = last_message_prompt
            response['last_message_reply'] = last_message_reply
        
        response['api_client_id'] = client_id

        if response['status'] == 'success':
            await self.__store_conversation(client_id=client_id, user=user, response=response) #Store conversation in database
            del response['api_instance_type']
            del response['api_instance_identity']

        return response

    async def process_reply_only(self, **kwargs) -> str:
        """
        Processes a reply only response from the API and returns a formatted string        
        """
        response: dict = kwargs.get('response', None)
        pretty: str = kwargs.get('pretty', 'false')
        if 'status' in response:
            if response['status'] == 'error':
                return response['message']
        if 'message' in response:
            if 'content' in response['message']:
                if 'parts' in response['message']['content']:
                    if len(response['message']['content']['parts']) >= 0:
                        well_formed_response = True
                        reply_only_response = response['message']['content']['parts'][0]
                        if pretty == "true":
                            md = markdown.Markdown(extensions=['fenced_code', 'nl2br', CodeHiliteExtension(linenums=True, guess_lang=True, use_pygmnet=True, css_class='highlight')])
                            reply_only_response = md.convert(reply_only_response)
                            reply_only_response = HTML_HEADER + reply_only_response + HTML_FOOTER
                            return reply_only_response
                        else:
                            return reply_only_response
                        
        if well_formed_response:
            return "Error: Malformed response"
    
    async def add_user(self, **kwargs) -> tuple:
        """
        Adds a user to the user database
        """
        await self.__load_api_users()
        client: str = kwargs.get('client', 'self')
        userid: str = kwargs.get('userid', None)
        username: str = kwargs.get('username', None)
        plus: bool = kwargs.get('plus', False)
        is_client: bool = kwargs.get('is_client', False)

        if client != 'self':
            client_id = self.users[client]['user_id']
        else:
            client_id = client

        if json_value_exists(Settings.API_KEYS, userid):
            status = 'error'
            message = 'User already exists'
            key = None
            return status, message, key
        else:
            api_key = generate_api_key()
            add_json_key(Settings.API_KEYS, {
                'user_id': userid,
                'username': username,
                'plus': plus,
                'clients': [client_id],
                'is_client': is_client,
            }, api_key)
            with open('./users.json', 'r', encoding="utf-8") as f:
                keys = json.load(f)
            keys['API_KEYS'] = Settings.API_KEYS
            with open('./users.json', 'w', encoding="utf-8") as f:
                json.dump(keys, f, ensure_ascii=False, indent=4)
            await self.__load_api_users()
            await Settings.reload_users()
            if json_value_exists(Settings.API_KEYS, userid):
                status = 'success'
                message = 'User added'
                key = api_key
                await self.__load_api_users()
                return status, message, key
            else:
                status = 'error'
                message = 'User not added'
                key = None
                return status, message, key