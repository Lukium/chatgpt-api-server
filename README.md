# chatgpt-api-server
ChatGPT Web API server Flask that can respond both via browser through Flask Forms and directly via POST/GET Requests

### To use:
1. Install everything in requirements.txt using `pip install -r ./requirements.txt`

2. Make necessary modofications to `settings.json` file:

	In `["openai"]["instnaces"]` add at least one account to be used as a built in account. You can add as many as you like by just adding additional keys. Each instance will be cycled through via the server.
	Each instance can also have it's own proxy by adding a `proxy` key. Proxies should be socks5 valid strings like `socks5://127.0.0.1:1080`

	Modify the `["api_server"]` key to match your needs:

	`"host"` `string` is the interface where your API should be accessible

	`"port"` `int` is the port where the API should be accessible

	`"default_proxy"` `string` is the default proxy to be used, and should be a valid socks5 string like `socks5://127.0.0.1:1080`

	Included in the folder /shinysocks is a basic windows socks5 server (see credits for more info)
	If running in linux, I recommend using `minisocks`

	`"wan_url"` `string` is the url the API will be accessible through if one has been setup (in dev)

	`"local_or_wan"` `string` is whether the API should be accessible via WAN or just LAN (should be `wan` or `lan`) (in dev)


3. Run `main.py` using `python ./main.py` (or whatever method available to you to run python scripts)
	This will create admin keys in your settings.json at first run, please make sure to keep these safe as they will have the power to add/remove users, access all cached conversations, etc.

4. Access the API by using either GET or POST request. You can also make the request via browser with the following format:
	The API has browser forms accessible via `/chat` endpoint for using chatgpt, `/access-token` for retrieving accesstokens and `/admin/add-user` for adding users
	The API has direct endpoints via `/api/chat` and `/api/access-token` for doing the same functions via POST/GET requests (add-user coming soon)

	Users can only use the API if they have been issued an API Key via `/admin/add-user`

	The endpoint will create a user in `./users.json` that include their API Key, username, userid, and whether they have access to plus builtin instances or not (as well as other future permissions)

	The following arguments are available for chat endpoints:

	`user`: (`API KEY`, default `none`) User's API Key (Not OpenAI but the one issued via `/admin/add-user`)

	`plus`: (`true` | `false` | `any`, default `false`) Will dictate whether to use a chatgpt plus instance during the request. If `true` or `any` (first available) is passed, a plus instance may be attempted and if the user doesn't have `plus` access in their credentials an exception may be thrown, therefore, users without access to plus should use `false`

	`prompt`: (`prompt test`, default: `prompt that lets user know they left it blank`) The prompt to be passed to chatgpt

	`reply_only`: (`true` | `false`, default: `true` on browser, `false` on `/api`) True will return just the chatgpt text reply, rather than json with all information

	`pretty`: (`true` | `false`, default: `true` on browser, `false` on `/api`) Only effective if `reply_only` = `true` Will determine whether to run the reply through markdown for better looking reply, especially useful for when using the API via the browser

	`access_token`: (`OpenAI Access Token`, default: None) When passed (This will essentially override `plus` with the `user_plus` parameter, since it will not be using a builtin instance), the API will create an instance of the `ChatGPT` class specifically using the access token to make a chatgpt request using the account associated with the access token rather than one of the accounts setup in `settings.json`. Access tokens can be retrieved using the `/access-token` or `/api/access-token` endpoints.

	`user_plus`: (`true` | `false`, default: `false`) Whether the account linked to the access_token has access to chatgpt Plus or not. Will determine which model to use, which may throw an exception if set to true when the user does not have access to to Plus

	### Credits:
	https://github.com/acheong08/OpenAIAuth OpenAIAuth - several modifications have been made to add functionality to the API

	https://github.com/acheong08/ChatGPT-Proxy - Basic information on how to process prompts to chatgpt
	
	https://github.com/jgaa/shinysocks - Basic Windows Proxy server



	
