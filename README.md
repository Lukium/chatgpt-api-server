# ChatGPT-api-server
ChatGPT Web API server Flask that can respond both via browser through Flask Forms and directly via POST/GET Requests

## Features:
### Multi Option Accessibility:
- POST/GET request for programmatic access
- WebUI browser access
### Flexibility:
- Replies can be either the full JSON or just the cut down reply
- Endpoints can be easily customized (changing the path) via settings file without any coding understanding needed
### Basic Permissions:
- Admin users can create (and soon remove) Client users or regular users
- Client users can create (and soon remove) regular users that it created
- Users can only use ChatGPT functionality.
- Users can be given access (or denied) to Plus ChatGPT accounts separately from free accounts.
### Account Support:
- Multi/Single built in ChatGPT Accounts, including Pro/Free accounts: accounts will be cycled on each request (follow ups will use the original account to keep conversation integrity)
- User account via Access Token (which can be retrieved via dedicated endpoint via email/password)
### Message Handling:
- In addition to the JSON from the ChatGPT reply, the API will also add additional information to the JSON, including the original prompt, the datetime the query was initiated; if a followup, the last message's prompt and reply, as well as a series of other useful information.
- All new conversations have a title automatically generated, which is also added to the JSON reply.
### User Conversation caching and followup:
- All user conversations are cached to the specific user.
- Users can recall either all conversations along with their titles or a single conversation including all messages within the conversation (both prompt and reply) sorted chronologically.
- When a conversation is followed up, the server will automatically use the account that was used to initiate the conversation, and use the last message in that conversation for the parent id, so as to maintain perfect conversation integrity. If the account used originally is not available, the user will receive an error.
### Client Support:
- "Client" users can be created by the admin, which can programmatically create API keys when necessary. For example: say you wanted to create a Discord Bot that interacts with the API. You could issue it a Client API key, and the bot will be able to automatically generate API keys for users that the bot has determined should be able to access the API.
### WebUI:
- WebUI can be used for all functionality, including chat, followup, access-token retrieval, API Key issuing.
- WebUI replies can be set to use markdown so they look cleaner.
- WebUI can also reply in pure JSON

## FOR EXPERIMENTAL AND LEARNING USE ONLY:
- I came up with this project while thinking of a use case where OpenAI, when providing its capabilities for an organization, say for example a University and its employees/students, rather than providing individual accounts that are managed by OpenAI, might instead provide a single account for the entire organization, such that the organization can then manage its own users via an API like the one I developed. 

- In this scenario, the individual's API key might be passed via the API to OpenAI for moderation and user counting, such that in turn, OpenAI can charge the organization based on the number of users utilizing the API via the org account. In this use case, the overall amount of resources used for user management is drastically reduced, since the organization would already have user records for each individual, which in my opinion, makes having OpenAI have a duplicate of records on its side redundant and generally a waste of resources. As a result, this setup would make the process more efficient for OpenAI in such a use case, reducing the resource usage for user authentication (one account vs potentially thousands), message storage (offloading it to the organization's server), and user billing (billing a single account instead of potentially thousands).

- For the Organization, this makes it further beneficial, as it provides it with more granular control of ChatGPT usage, including the ability to check if a user might have committed plagiarism, since it would, in case of a suspicion, be able to verify the user's message cache. Furthermore, OpenAI, having saved in resources, might be able to pass on some of those savings to the org in the way of cheaper per/user cost, making it a win for both sides.

### To use:
1. Install everything in requirements.txt using `pip install -r ./requirements.txt`

2. Make necessary modifications to `settings.json` file:

	In `["OpenAI"]["instances"]` add at least one account to be used as a built in account. You can add as many as you like by just adding additional keys. Each instance will be cycled through via the server.
	Each instance can also have it's own proxy by adding a `proxy` key. Proxies should be socks5 valid strings like `socks5://127.0.0.1:1080`

	Modify the `["api_server"]` key to match your needs:

	`"host"` `string` is the interface where your API should be accessible

	`"port"` `int` is the port where the API should be accessible

	`"default_proxy"` `string` is the default proxy to be used, and should be a valid socks5 string like `socks5://127.0.0.1:1080`

	Included in the folder /shinysocks is a basic windows socks5 server (see credits for more info)
	If running in linux, I recommend using `microsocks` https://github.com/rofl0r/microsocks

	`"wan_url"` `string` is the url the API will be accessible through if one has been setup (in dev)

	`"local_or_wan"` `string` is whether the API should be accessible via WAN or just LAN (should be `wan` or `lan`) (in dev)


3. Run `main.py` using `python ./main.py` (or whatever method available to you to run python scripts)
	This will create admin keys in your settings.json at first run, please make sure to keep these safe as they will have the power to add/remove users, access all cached conversations, etc.

4. Access the API by using either GET or POST request. You can also make the request via browser with the following format:
	The API has browser forms accessible via `/chat` endpoint for using ChatGPT, `/access-token` for retrieving access tokens and `/admin/add-user` for adding users
	The API has direct endpoints via `/api/chat` and `/api/access-token` for doing the same functions via POST/GET requests (add-user coming soon)

	Users can only use the API if they have been issued an API Key via `/admin/add-user`

	The endpoint will create a user in `./users.json` that include their API Key, username, userID, and whether they have access to plus builtin instances or not (as well as other future permissions)

	The following arguments are available for chat endpoints:

	`user`: (`API KEY`, default `none`) User's API Key (Not OpenAI but the one issued via `/admin/add-user`)

	`plus`: (`true` | `false` | `any`, default `false`) Will dictate whether to use a ChatGPT plus instance during the request. If `true` or `any` (first available) is passed, a plus instance may be attempted and if the user doesn't have `plus` access in their credentials an exception may be thrown, therefore, users without access to plus should use `false`

	`prompt`: (`prompt test`, default: `prompt that lets user know they left it blank`) The prompt to be passed to ChatGPT

	`reply_only`: (`true` | `false`, default: `true` on browser, `false` on `/api`) True will return just the ChatGPT text reply, rather than json with all information

	`pretty`: (`true` | `false`, default: `true` on browser, `false` on `/api`) Only effective if `reply_only` = `true` Will determine whether to run the reply through markdown for better looking reply, especially useful for when using the API via the browser

	`access_token`: (`OpenAI Access Token`, default: None) When passed (This will essentially override `plus` with the `user_plus` parameter, since it will not be using a builtin instance), the API will create an instance of the `ChatGPT` class specifically using the access token to make a ChatGPT request using the account associated with the access token rather than one of the accounts setup in `settings.json`. Access tokens can be retrieved using the `/access-token` or `/api/access-token` endpoints.

	`user_plus`: (`true` | `false`, default: `false`) Whether the account linked to the access_token has access to ChatGPT Plus or not. Will determine which model to use, which may throw an exception if set to true when the user does not have access to to Plus

	### Credits:
	https://github.com/acheong08/OpenAIAuth OpenAIAuth - several modifications have been made to add functionality to the API

	https://github.com/acheong08/ChatGPT-Proxy - Basic information on how to process prompts to ChatGPT
	
	https://github.com/jgaa/shinysocks - Basic Windows Proxy server



	
