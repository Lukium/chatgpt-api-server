#IMPORT BUILT-IN LIBRARIES
from datetime import datetime
import json
import uuid

#IMPORT THIRD-PARTY LIBRARIES
import tls_client

#IMPORT CONTRIBUTED-CODE LIBRARIES
from contrib.OpenAIAuth.OpenAIAuth import OpenAIAuth
from contrib.OpenAIAuth.Cloudflare import Cloudflare


import settings.Settings as Settings

from helpers.General import is_valid_socks5_url

class ChatGPT:
    def __init__(self, **kwargs) -> None:
        self.instance = kwargs.get('instance')
        self.cf_clearance = kwargs.get('cf_clearance')
        self.user_agent = kwargs.get('user_agent')
        self.type = kwargs.get('type', 'builtin')
        self.user_access_token = kwargs.get('user_access_token', None)
        self.user_plus = kwargs.get('user_plus', 'false')
        
        self.session = tls_client.Session(client_identifier='chrome_108')
    
    @classmethod
    async def create(cls, **kwargs):
        instance = kwargs.get('instance')
        cf_clearance = kwargs.get('cf_clearance')
        user_agent = kwargs.get('user_agent')
        type = kwargs.get('type', 'builtin')
        user_access_token = kwargs.get('user_access_token', None)
        user_plus = kwargs.get('user_plus', 'false')
        
        self = cls(instance=instance, cf_clearance=cf_clearance, user_agent=user_agent, type=type, user_access_token=user_access_token, user_plus=user_plus)
        
        if type == 'builtin':
            await self.__configure()
            await self.__login()
        elif type == 'user':
            await self.__configure_user()
            await self.__refresh()
        return self

    async def __configure_user(self):
        self.access_token = self.user_access_token
        with open('./settings.json', 'r') as f:
            settings = json.load(f)
        api_server_settings = settings['api_server']
        #Make sure the instance has a proxy in settings.json either under "opeanai" or under "api_server"
        if "default_proxy" in api_server_settings:
            proxy = api_server_settings.get("default_proxy")
        else:
            raise Exception(f'Instance {self.instance} has no proxy set, and no default proxy was found in settings.json in the "api_server" section')
        if type(proxy) is not str:
            raise Exception(f'Proxy for instance {self.instance} was found in settings.json, but it must be a string')
        else:
            if not is_valid_socks5_url(proxy):
                raise Exception(f'Proxy for instance {self.instance} was found in settings.json, but it is not a valid SOCKS5 proxy')
            else:
                self.proxy = proxy
                proxies = {
                    "http": self.proxy,
                    "https": self.proxy
                }
                self.session.proxies.update(proxies)
        #Make sure whether the instance has a plus account or not and set the attribute        
        self.plus = self.user_plus

    
    async def __configure(self):
        with open('./settings.json', 'r') as f:
            settings = json.load(f)
        instance_settings = settings['openai']['instances'][self.instance]      
        api_server_settings = settings['api_server']

        #Make sure the instance has an email
        if "email" not in instance_settings:
            raise Exception(f'No email was found for instance {self.instance} in settings.json')        
        self.email = instance_settings.get("email")

        #Make sure the instance has a password
        if "password" not in instance_settings:
            raise Exception(f'No password was found for instance {self.instance} in settings.json')
        self.password = instance_settings.get("password")

        #Make sure the instance has a proxy in settings.json either under "opeanai" or under "api_server"
        if "proxy" in instance_settings:
            if instance_settings.get("proxy") == "default":
                if "default_proxy" in api_server_settings:
                    proxy = api_server_settings.get("default_proxy")
                else:
                    raise Exception(f'Instance {self.instance} has proxy set to default, but no default proxy was found in settings.json in the "api_server" section')
            else:
                proxy = instance_settings.get("proxy")
        else:
            if "default_proxy" in api_server_settings:
                proxy = api_server_settings.get("default_proxy")
            else:
                raise Exception(f'Instance {self.instance} has no proxy set, and no default proxy was found in settings.json in the "api_server" section')
        if type(proxy) is not str:
            raise Exception(f'Proxy for instance {self.instance} was found in settings.json, but it must be a string')
        else:
            if not is_valid_socks5_url(proxy):
                raise Exception(f'Proxy for instance {self.instance} was found in settings.json, but it is not a valid SOCKS5 proxy')
            else:
                self.proxy = proxy
                proxies = {
                    "http": self.proxy,
                    "https": self.proxy
                }
                self.session.proxies.update(proxies)        
        
        #Make sure whether the instance has a plus account or not and set the attribute
        if "plus" in instance_settings:
            if type(instance_settings.get("plus")) is not bool:
                raise Exception(f'Attribute "plus" for instance {self.instance} was found in settings.json, but it must be a boolean')
            else:
                self.plus = instance_settings.get("plus")
        else:
            raise Exception(f'No "plus" attribute was found for instance {self.instance} in settings.json, please add it and set it to either true or false')

    async def __refresh(self):
        """
        Refreshes the session's cookies and headers with the latest available information from login()
        """
        self.session.cookies.clear()
        self.session.cookies.update(
            {
                "cf_clearance": self.cf_clearance,
                #"__Secure-next-auth.session-token": self.session_token
            }
        )
            
        self.session.headers.clear()
        self.session.headers.update(
            {
                #"Accept": "text/event-stream",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": self.user_agent,
                "Content-Type": "application/json",
                "X-Openai-Assistant-App-Id": "",
                "Connection": "close",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://chat.openai.com/chat",
            },
        )

    async def __login(self):
        auth = OpenAIAuth(
            email_address=self.email,
            password=self.password,
            proxy=self.proxy
        )
        await auth.begin()
        self.access_token = await auth.get_access_token()
        self.session_token = await auth.get_session_token()
        await self.__refresh()
    
    async def __response_check(self, response_text: str):
        try: #If response has errors, the response should be a json string
            response_to_check = json.loads(response_text)
            expired_cookies_warning = '<div id="no-cookie-warning" class="cookie-warning" style="display:none">'
            if "detail" in response_to_check:
                status = "error"
                message = response_to_check["detail"]
                return status, message
            elif expired_cookies_warning in response_to_check:
                status = "error"
                message = "Cookies Expired, run refresh_cloudflare()"
                return status, message
            else:
                status = "unknown error"
                message = json.dumps(response_to_check, indent=4)
                return status, message
        except: #If response is good, the response should be a string which will cause an error when trying to load it as json
            status = "success"
            message = "No Errors"
            return status, message
    
    async def refresh_cloudflare():
        Settings.API_CF_CLEARANCE, Settings.API_USER_AGENT = await Cloudflare(proxy=Settings.API_DEFAULT_PROXY).a_get_cf_cookies()
        if len(Settings.chatgpt_instances) > 0:
            for instance in Settings.chatgpt_instances:
                instance.cf_clearance = Settings.API_CF_CLEARANCE
                instance.user_agent = Settings.API_USER_AGENT
        if len(Settings.chatgpt_free_instances) > 0:
            for instance in Settings.chatgpt_free_instances:
                instance.cf_clearance = Settings.API_CF_CLEARANCE
                instance.user_agent = Settings.API_USER_AGENT
        if len(Settings.chatgpt_plus_instances) > 0:
            for instance in Settings.chatgpt_plus_instances:
                instance.cf_clearance = Settings.API_CF_CLEARANCE
                instance.user_agent = Settings.API_USER_AGENT
    
    async def cloudflare(self):
        self.cf_clearance = Settings.API_CF_CLEARANCE
        self.user_agent = Settings.API_USER_AGENT

    async def login(self):
        auth = OpenAIAuth(
            email_address=self.email,
            password=self.password,            
            proxy=self.proxy
        )        
        await auth.begin()
        self.access_token = await auth.get_access_token()
        self.session_token = await auth.get_session_token()
        await self.cloudflare()
        await self.__refresh()

    async def __chatgpt_post(self, request_body: dict):
        response = self.session.post(
        url = "https://chat.openai.com/backend-api/conversation",
        headers = self.session.headers,
        cookies = self.session.cookies,
        data = json.dumps(request_body),
        timeout_seconds = 360
        )
        return response
     
    async def ask(self, prompt: str = None, turbo: bool = False):

        message_id = str(uuid.uuid4())
        prompt = prompt
        if self.plus == True:
            if turbo == True:
                model = "text-davinci-002-render-sha"
            else:
                model = "text-davinci-002-render-paid"
        else:
            model = "text-davinci-002-render"
        
        request_body = {
        "action": "next",
        "messages": [
            {
                "id": message_id,
                "role": "user",
                "content": {
                    "content_type": "text",
                    "parts": [
                        prompt
                    ]
                }
            }
        ],
        "parent_message_id": "",
        "model": model
    }
        
        start_time = datetime.now() #Start counting time

        response = await self.__chatgpt_post(request_body)

        response_status = await self.__response_check(response.text)
        if response_status[0] == "error":
            response: dict = {}
            if response_status[1] == "Cookies Expired, run refresh_cloudflare()":
                await self.refresh_cloudflare()
                if self.type == 'user':
                    await self.__refresh()
                response = await self.__chatgpt_post(request_body)
                response_status = await self.__response_check(response.text)
                if response_status[0] == "error":
                    if response_status[1] == "Cookies Expired, run refresh_cloudflare()":
                        response["status"] = response_status[0]
                        response["message"] = 'Cookies appear to be expired even after refreshing them. Please contact Admin.'
            else:
                response["status"] = response_status[0]
                response["message"] = response_status[1]
        else:
            step_1 = str(response.text).replace("data: [DONE]","").strip() # Remove the "data: [DONE]" from the response as well as leading and trailing whitespace
            step_2 = step_1.rfind('data: {"message": {"id": "') # Find the last occurance of the string (data: {"message": {"id": ") in the response
            step_3 = (step_1[step_2:]).strip() # Slice the response from the last occurance of the string (data: {"message": {"id": ") to the end of the response and remove leading and trailing whitespace
            step_4 = step_3.find(' ') # Find the first occurance of a space in the response
            step_5 = (step_3[step_4:]).strip() # Slice the response from the beginning of the response to the first occurance of a space and remove leading and trailing whitespace
            response = json.loads(step_5) # Convert the response to a dictionary
        
        end_time = datetime.now() #Start counting time
        response_time = str(round((end_time - start_time).total_seconds(), 2)) #Calculate time difference
        
        response["response_time_taken"] = response_time #Add response time to response object
        response['prompt_time_origin'] = start_time.strftime("%Y-%m-%d | %H:%M:%S")
        response["prompt"] = prompt #Add prompt to response object

        return response