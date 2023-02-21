#IMPORT BUILT-IN LIBRARIES
import json

#IMPORT THIRD-PARTY LIBRARIES
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension

#IMPORT CONTRIBUTED-CODE LIBRARIES
from contrib.OpenAIAuth.OpenAIAuth import OpenAIAuth

#IMPORT CLASSES
from classes.ChatGPT import ChatGPT

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
        await self.__load_api_users()
        await self.__load_conversations()
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
    
    async def __load_api_users(self) -> dict:
        with open('./users.json', 'r') as f:
            users = (json.load(f))['API_KEYS']
        self.users = users
    
    async def __load_conversations(self) -> dict:
        with open('./conversations.json', 'r') as f:
            conversations = (json.load(f))['users']
        self.conversations = conversations

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
    
    async def __spawn_user_chatgpt(self, **kwargs) -> ChatGPT:
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
            'conversation_message_index': response['conversation_message_index']
        }

        with open('conversations.json', 'r') as f:
            conversations = json.load(f)
        if user_id not in conversations['users']:
            add_json_key(conversations['users'], {'username': Settings.API_KEYS[user]['username'], 'conversations': {}}, user_id)
            
        if conversation_id not in conversations['users'][user_id]['conversations']:
            add_json_key(conversations['users'][user_id]['conversations'], {'title': response['conversation_title'], 'api_instance_type': response['api_instance_type'], 'api_instance': response['api_instance_identity'], 'messages': {}}, conversation_id)

        if message_id not in conversations['users'][user_id]['conversations'][conversation_id]['messages']:
            add_json_key(conversations['users'][user_id]['conversations'][conversation_id]['messages'], data, message_id)

        with open('conversations.json', 'w') as f:
            json.dump(conversations, f, indent=4)
        
        await self.__load_conversations()

    async def recall(self, **kwargs) -> str:
        user: str = kwargs.get('user', None)
        conversation_id: str = kwargs.get('conversation_id', "")
        user_id = self.users[user]['user_id']
        user_conversations = self.conversations[user_id]['conversations']

        response = {}
        if conversation_id == "":
            for key in user_conversations:
                response[key] = {
                    'title': user_conversations[key]['title'],
                }
        else:
            response['conversation_id'] = conversation_id
            response['conversation_title'] = user_conversations[conversation_id]['title']

            tuple_list = [(key, value) for key, value in user_conversations[conversation_id]['messages'].items()]
            sorted_tuple_list = sorted(tuple_list, key=lambda x: x[1]["conversation_message_index"])
            sorted_list = [x for x in sorted_tuple_list]
            for message in sorted_list:
                message[1].pop('conversation_message_index')
                message[1].pop('origin_time')
            final_list: list = []
            for message in sorted_list:
                dict = {
                    message[0] : message[1]
                }
                final_list.append(dict)
            response['messages'] = final_list
        
        response = json.dumps(response, indent=4)
        
        return response

    async def process_chagpt_request(self, **kwargs) -> dict:
        user: str = kwargs.get('user', None)
        prompt: str = kwargs.get('prompt', Settings.API_DEFAULT_PROMPT)
        conversation_id: str = kwargs.get('conversation_id', "")
        parent_message_id: str = kwargs.get('parent_message_id', "")
        plus: str = kwargs.get('plus', 'any')
        type: str = kwargs.get('type', 'builtin')
        access_token: str = kwargs.get('access_token', None)
        user_plus: str = kwargs.get('user_plus', 'false')

        chatgpt: ChatGPT = None #Initialize ChatGPT instance

        response: dict = {}
        followup: bool = False

        print (parent_message_id)

        if conversation_id != "" and conversation_id is not None:
            followup = True
            user_id = self.users[user]['user_id']
            #Check if conversation exists
            if conversation_id not in self.conversations[user_id]['conversations']:
                response['status'] = 'error'
                response['message'] = 'Conversation not found. It either does not exist or has been purged from the cache. Please try again with a new conversation id or start a new conversation.'
                return response
            else:
                conversation = self.conversations[user_id]['conversations'][conversation_id]
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
            
            #Check if parent message exists
            if parent_message_id == "":
                response['status'] = 'error'
                response['message'] = 'No parent message id specified. Please try again'
                return response
            
            #Check if parent message exists within conversation
            if parent_message_id not in conversation['messages']:
                response['status'] = 'error'
                response['message'] = 'Parent message id not found within provided coversation id. It may have been purged from the cache. Please try again with a more recent message or start a new conversation.'
                return response
            
            #Check if parent message id matches last message id in conversation
            conversation_length = len(conversation['messages']) #Get length of conversation
            conversation_message_index = conversation_length #Get index of next message based on length of conversation
            conversation_messages: list = list(conversation['messages'].keys()) #Get list of all messages in conversation
            conversation_last_message_id = max(conversation_messages, key=lambda k: self.conversations[user_id]['conversations'][conversation_id]['messages'][k]['conversation_message_index']) #Get last message key based on message index of each message in conversation
            if conversation_last_message_id != parent_message_id:
                response['status'] = 'error'
                response['message'] = 'Parent message id does not match the last message id in the conversation. Please try again with the last message id or start a new conversation.'
                return response
            
            #Get last message prompt and reply from conversation and append to response
            last_message_prompt = conversation['messages'][parent_message_id]['prompt']
            last_message_reply = conversation['messages'][parent_message_id]['reply']
        
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

        response: dict = await chatgpt.ask(user=user, prompt=prompt, conversation_id=conversation_id, parent_message_id=parent_message_id)        

        if followup:
            response['conversation_message_index'] = conversation_message_index
            response['conversation_title'] = conversation_title
            response['last_message_prompt'] = last_message_prompt
            response['last_message_reply'] = last_message_reply
        else:
            response['conversation_message_index'] = 0

        if response['status'] == 'success':
            await self.__store_conversation(user=user, response=response) #Store conversation in database
        
        del response['api_instance_type']
        del response['api_instance_identity']

        return response

    async def process_reply_only(self, **kwargs) -> str:
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

    
    async def __reload_users(self):
        """
        Reloads the API user database
        """
        with open('./users.json', 'r') as f:
            keys = json.load(f)
        Settings.API_KEYS = keys['API_KEYS']
    
    async def add_user(self, **kwargs):
        """
        Adds a user to the user database
        """
        userid: str = str(kwargs['userid'])
        username: str = str(kwargs['username'])
        plus: bool = kwargs['plus']

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
            }, api_key)
            with open('./users.json', 'r') as f:
                keys = json.load(f)
            keys['API_KEYS'] = Settings.API_KEYS
            with open('./users.json', 'w') as f:
                json.dump(keys, f, indent=4)
            await self.__reload_users()
            await Settings.reload_users()
            if json_value_exists(Settings.API_KEYS, userid):
                status = 'success'
                message = 'User added'
                key = api_key
                return status, message, key
            else:
                status = 'error'
                message = 'User not added'
                key = None
                return status, message, key