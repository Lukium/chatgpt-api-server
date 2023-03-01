from helpers.General import add_json_key

class ChatGPTClient:
    def __init__ (self, **kwargs) -> None:
        identity = kwargs.get('identity', None)
        self.users: dict = {}
        self.user_ids: list = []
        self.identity: str = identity
        
    @classmethod
    async def create(cls, **kwargs) -> 'ChatGPTClient':
        server_users: dict = kwargs.get('server_users', {})
        client_users: list = kwargs.get('client_users', [])
        client_id: str = kwargs.get('client_id', None)
        self = cls(identity = client_id)
        await self.__load_client_users(client_users = client_users, server_users = server_users)
        return self
    
    async def __load_client_users(self, **kwargs) -> None:
        
        client_users = kwargs.get('client_users', [])
        server_users = kwargs.get('server_users', {})
        
        if len(client_users) == 0:
            return
        else:
            self.users = {}
            for user in client_users:
                self.users[user] = server_users[user]
                self.user_ids.append(server_users[user]['user_id'])