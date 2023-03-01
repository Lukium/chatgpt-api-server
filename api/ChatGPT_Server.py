#IMPORT BUILT-IN LIBRARIES
import asyncio
import json

#IMPORT THIRD-PARTY LIBRARIES
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template, redirect, url_for
from flask_bootstrap import Bootstrap

#IMPORT CLASSES
from classes.ChatGPTServer import ChatGPTServer

#IMPORT FORMS
from forms.FormChatGPT import FormChatGPT
from forms.FormAddUser import FormAddUser
from forms.FormAccessToken import FormAccessToken
from forms.FormChatRecall import FormChatRecall

#IMPORT SETTINGS
import settings.Settings as Settings
from settings.Settings import LANG

#SETUP FLASK APP
app = Flask(__name__)
app.config['SECRET_KEY'] = Settings.API_APP_SECRET
Bootstrap(app)

ChatGPTServer = asyncio.run(ChatGPTServer.create())
    
#SETUP ROUTES
@app.route(Settings.ENDPOINT_API_CHATGPT, methods=["GET", "POST"])
async def api_chat():
    response: dict = {}

    if request.method == "GET":
        prompt = request.args.get("prompt", Settings.API_DEFAULT_PROMPT)
        client = request.args.get("client", None)
        user = request.args.get("user", None)
        user_id = request.args.get("user_id", None)
        username = request.args.get("username", None)
        user_id_plus = request.args.get("user_id_plus", None)
        conversation_id = request.args.get("conversation_id", None)
        plus = request.args.get("plus", "false")
        reply_only = request.args.get("reply_only", "false")
        pretty = request.args.get("pretty", "false")
        access_token = request.args.get("access_token", None)
        user_plus = request.args.get("user_plus", "false")
    elif request.method == "POST":
        prompt = request.json.get("prompt", Settings.API_DEFAULT_PROMPT)
        client = request.json.get("client", None)
        user = request.json.get("user", None)
        user_id = request.json.get("user_id", None)
        username = request.json.get("username", None)
        user_id_plus = request.json.get("user_id_plus", None)
        conversation_id = request.json.get("conversation_id", None)
        plus = request.json.get("plus", "false")
        reply_only = request.json.get("reply_only", "false")
        pretty = request.json.get("pretty", "false")
        access_token = request.json.get("access_token", None)
        user_plus = request.json.get("user_plus", "false")

    Skip_User_Check = False
    #Perform Client Check if client is provided
    if client is not None:
        client_check = await ChatGPTServer.check_client(user=client)        
        if client_check['status'] == 'error':
            return client_check, 400 #Return Error Message if Client is Invalid
        else:
            if user is None:
                if user_id is None or username is None or user_id_plus is None:
                    response = {
                        "status": "error",
                        "message": "[user_id], [username] and [user_id_plus] are required if [client] is provided and [user] is not provided"
                    }
                    return response, 400 #Return Error Message if User ID, Username and User ID Plus are not provided
            client_user_id_check: dict = await ChatGPTServer.client_user_id_check(client=client, user_id=user_id, username=username, user_id_plus=user_id_plus)
            if client_user_id_check['status'] == 'error':
                return client_user_id_check, 400 #Return Error Message if Client User ID Check is Invalid
            else:
                user = client_user_id_check['key']
                Skip_User_Check = True                

    
    #Perform User Check
    if not Skip_User_Check:
        user_check = await ChatGPTServer.check_user(user=user)
        if user_check['status'] == 'error':
            return user_check, 400 #Return Error Message if User is Invalid
    
    if access_token != "" and access_token is not None:
        response: dict = await ChatGPTServer.process_chagpt_request(
            client=client,
            user=user,
            prompt=prompt,
            conversation_id=conversation_id,
            type='user',
            access_token=access_token,
            user_plus=user_plus
            )
    else:
        response: dict = await ChatGPTServer.process_chagpt_request(
            client=client,
            user=user,
            prompt=prompt,
            conversation_id=conversation_id,
            plus=plus
            )
            
    if reply_only == "true":
        response = await ChatGPTServer.process_reply_only(
            response=response,
            pretty=pretty
            )
        
    return response, 200

@app.route(Settings.ENDPOINT_BROWSER_CHATGPT, methods=["GET", "POST"])
async def chat():
    form = FormChatGPT()
    user = request.args.get("user", None)
    access_token = request.args.get("access_token", None)
    if user is not None and user != "":
        form.api_key.data = user
    if access_token is not None:
        form.access_token.data = access_token

    title = f'{LANG["htmls"]["index"]["title"]}'
    message_under_title = f'{LANG["htmls"]["index"]["message_under_title"]}'
    action_instruction = f'{LANG["htmls"]["index"]["action_instruction"]}'
    message_after_submit_1 = f'{LANG["htmls"]["index"]["message_after_submit_1"]}'
    message_after_submit_2 = f'{LANG["htmls"]["index"]["message_after_submit_2"]}'

    if form.validate_on_submit():
        #Perform User Check
        user_check = await ChatGPTServer.check_user(user=form.api_key.data)
        if user_check['status'] == 'error':
            return user_check, 400 #Return Error Message if User is Invalid

        if form.access_token.data != "":
            response: dict = await ChatGPTServer.process_chagpt_request(
                user=form.api_key.data,
                prompt=form.prompt.data,
                conversation_id=form.conversation_id.data,
                type='user',
                access_token=form.access_token.data,
                user_plus=form.user_plus.data
                )
        else:
            response: dict = await ChatGPTServer.process_chagpt_request(
                user=form.api_key.data,
                prompt=form.prompt.data,
                conversation_id=form.conversation_id.data,
                plus=form.plus.data
                )
        
        if form.reply_only.data == "true":
            response = await ChatGPTServer.process_reply_only(
                response=response,
                pretty=form.pretty.data
                )
            
        return response, 200
    return render_template(
        "index.html",
        form=form, title=title,
        message_under_title=message_under_title,
        action_instruction=action_instruction,
        message_after_submit_1=message_after_submit_1,
        message_after_submit_2=message_after_submit_2
    )

@app.route(Settings.ENDPOINT_API_CHATRECALL, methods=["GET", "POST"])
async def api_recall():

    if request.method == "GET":
        client = request.args.get("client", None)
        user = request.args.get("user", None)
        conversation_id = request.args.get("conversation_id", None)
    elif request.method == "POST":
        client = request.json.get("client", None)
        user = request.json.get("user", None)
        conversation_id = request.json.get("conversation_id", None)

    #Perform Client Check if client is provided
    if client is not None:
        client_check = await ChatGPTServer.check_client(user=client)
        if client_check['status'] == 'error':
            return client_check, 400 #Return Error Message if Client is Invalid

    #Perform User Check
    user_check = await ChatGPTServer.check_user(user=user)
    if user_check['status'] == 'error':
        return user_check, 400 #Return Error Message if User is Invalid
    
    if conversation_id is None or conversation_id == "":
        response = await ChatGPTServer.recall(client=client, user=user)
    else:
        response = await ChatGPTServer.recall(client=client, user=user, conversation_id=conversation_id)
    
    return response, 200

@app.route(Settings.ENDPOINT_BROWSER_CHATRECALL, methods=["GET", "POST"])
async def chat_recall():
    form = FormChatRecall()
    user = request.args.get("user", None)
    if user is not None and user != "":
        form.api_key.data = user

    title = f'{LANG["htmls"]["recall"]["title"]}'
    message_under_title = f'{LANG["htmls"]["recall"]["message_under_title"]}'
    action_instruction = f'{LANG["htmls"]["recall"]["action_instruction"]}'

    if form.validate_on_submit():
        #Perform User Check
        user_check = await ChatGPTServer.check_user(user=form.api_key.data)
        if user_check['status'] == 'error':
            return user_check, 400 #Return Error Message if User is Invalid
        
        conversation_id = form.conversation_id.data
        if conversation_id is None or conversation_id == "":
            response = await ChatGPTServer.recall(user=form.api_key.data)
        else:
            response = await ChatGPTServer.recall(user=form.api_key.data, conversation_id=conversation_id)
        
        return response, 200

    return render_template(
        "recall.html",
        form=form,
        title=title,
        message_under_title=message_under_title,
        action_instruction=action_instruction
        )
    
@app.route(Settings.ENDPOINT_API_ACCESS_TOKEN, methods=["GET", "POST"])
async def api_access_token():
    if request.method == 'GET':
        user = request.args.get('user', None)
        email = request.args.get('email', None)
        password = request.args.get('password', None)
    elif request.method == 'POST':
        user = request.json.get('user', None)
        email = request.json.get('email', None)
        password = request.json.get('password', None)
    
    if user is not None and email is not None and password is not None:
        user_check = await ChatGPTServer.check_user(user=user)
        if user_check['status'] == 'error':
            return user_check, 400 #Return Error Message if User is Invalid
        
        access_token = await ChatGPTServer.retrieve_access_token(email=email, password=password)  
        if access_token == 'Wrong email or password provided':
            response = json.loads(f'{{"Error": "{access_token}"}}')
        else:        
            response = json.loads(f'{{"Access Token": "{access_token}"}}')
        return response, 200
    elif user is None:
        response = json.loads('{"Error": "Please provide a valid user."}')
        return response, 400
    elif email is None:
        response = json.loads('{"Error": "Please provide a valid email."}')
        return response, 400
    elif password is None:
        response = json.loads('{"Error": "Please provide a valid password."}')
        return response, 400

@app.route(Settings.ENDPOINT_BROWSER_ACCESS_TOKEN, methods=["GET", "POST"])
async def access_token():
    form = FormAccessToken()
    user = request.args.get("user", None)
    if user is not None and user != "":
        form.api_key.data = user
    
    title = f'{LANG["htmls"]["access_token"]["title"]}'
    message_under_title = f'{LANG["htmls"]["access_token"]["message_under_title"]}'
    action_instruction = f'{LANG["htmls"]["access_token"]["action_instruction"]}'
    message = f'{LANG["htmls"]["access_token"]["message"]}'

    message = f'This will retrieve your current ChatGPT OpenAI Access Token using your ChatGPT Email and Password.'    
    if form.validate_on_submit():
        user = form.api_key.data
        email = form.email.data
        password = form.password.data

        #Perform User Check
        user_check = await ChatGPTServer.check_user(user=user)
        if user_check['status'] == 'error':
            return user_check, 400 #Return Error Message if User is Invalid
        
        access_token = await ChatGPTServer.retrieve_access_token(email=email, password=password)  
        if access_token == 'Wrong email or password provided':
            response = json.loads(f'{{"Error": "{access_token}"}}')
        else:        
            response = json.loads(f'{{"Access Token": "{access_token}"}}')
        return response, 200

    return render_template(
        "access-token.html",
        form=form,
        title=title,
        message_under_title=message_under_title,
        action_instruction=action_instruction,
        message=message)

@app.route(Settings.ENDPOINT_BROWSER_ADD_USER, methods=["GET", "POST"])
async def add_user():
    response: dict = {}
    admin = request.args.get("admin", None)
    client = request.args.get("client", None)

    title = f'{LANG["htmls"]["add_user"]["title"]}'
    message_under_title = f'{LANG["htmls"]["add_user"]["message_under_title"]}'
    action_instruction = f'{LANG["htmls"]["add_user"]["action_instruction"]}'

    if admin is not None and admin != "":
        admin_check = await ChatGPTServer.check_admin(user=admin)
        if admin_check['status'] == 'error':
            return admin_check, 400 #Return Error Message if Admin is Invalid
        else:
            admin = True
    
    if client is not None and client != "":
        client_check = await ChatGPTServer.check_client(user=client)
        if client_check['status'] == 'error':
            return client_check, 400 #Return Error Message if Client is Invalid
        else:
            client = True
    
    if not admin and not client:
        response['status'] = 'error'
        response['message'] = 'No valid Admin or Client API Key provided'
        return jsonify(response), 400    
    else:
        form = FormAddUser()
        if form.validate_on_submit():
            userid = form.userid.data
            username = form.username.data
            plus = form.plus.data
            new_user_is_client = form.is_client.data

            if plus == "true":
                plus = True
            elif plus == "false":
                plus = False
            if new_user_is_client == "true":
                new_user_is_client = True
            elif new_user_is_client == "false":
                new_user_is_client = False

            if client:
                if new_user_is_client:
                    response['status'] = 'error'
                    response['message'] = 'Clients cannot create new clients'
                    return jsonify(response), 400            
            
            status, message, key = await ChatGPTServer.add_user(userid=userid, username=username, plus=plus, is_client=new_user_is_client)
            response['status'] = status
            response['message'] = message
            response['api_key'] = key
            if status == 'error':
                return jsonify(response), 422
            else:
                return jsonify(response), 200
        return render_template(
            "admin/add-user.html",
            title=title,
            message_under_title=message_under_title,
            action_instruction=action_instruction,
            form=form)

@app.route(Settings.ENDPOINT_API_REMOVE_CONVERSATION, methods=["GET", "POST"])
async def api_remove_conversation() -> dict:
    response: dict = {}
    if request.method == 'GET':
        admin = request.args.get('admin', None)
        client = request.args.get('client', None)
        user = request.args.get('user', None)
        user_id = request.args.get('user_id', None)
        conversation_id = request.args.get('conversation_id', None)
    elif request.method == 'POST':
        admin = request.json.get('admin', None)
        client = request.json.get('client', None)
        user = request.json.get('user', None)
        user_id = request.json.get('user_id', None)
        conversation_id = request.json.get('conversation_id', None)
    
    is_admin = False
    is_client = False
    is_user = False

    if admin is not None and admin != "":
        admin_check = await ChatGPTServer.check_admin(user=admin)
        if admin_check['status'] == 'error':
            return admin_check, 400 #Return Error Message if Admin is Invalid
        else:
            is_admin = True

    
    Skip_User_Check = False
    #Perform Client Check if client is provided
    if client is not None:
        client_check = await ChatGPTServer.check_client(user=client)        
        if client_check['status'] == 'error':
            return client_check, 400 #Return Error Message if Client is Invalid
        else:
            is_client = True
            if user is None:
                if user_id is None:
                    response = {
                        "status": "error",
                        "message": "[user_id] is required if [client] is provided and [user] is not provided"
                    }
                    return response, 400 #Return Error Message if User ID, Username and User ID Plus are not provided
                get_user_from_user_id: dict = await ChatGPTServer.get_user_from_user_id(user_id=user_id)
                if get_user_from_user_id['status'] == 'error':
                    return get_user_from_user_id, 400 #Return Error Message if Client User ID Check is Invalid
                else:
                    user = get_user_from_user_id['user']
                    is_user = True                
                    Skip_User_Check = True

    if not Skip_User_Check:
        if user is not None and user != "":
            user_check = await ChatGPTServer.check_user(user=user)
            if user_check['status'] == 'error':
                return user_check, 400 #Return Error Message if User is Invalid
            else:
                is_user = True
    
    if not is_admin and not is_client and not is_user:
        response['status'] = 'error'
        response['message'] = 'No valid Admin, Client or User provided'
        return jsonify(response), 400
    else:
        response: dict = await ChatGPTServer.remove_conversation(user=user, conversation_id=conversation_id)
        return jsonify(response), 200


@app.route(Settings.ENDPOINT_API_ADD_USER, methods=["GET", "POST"])
async def api_add_user():
    response: dict = {}
    if request.method == 'GET':
        admin = request.args.get('admin', None)
        client = request.args.get('client', None)
        userid = request.args.get('userid', None)
        username = request.args.get('username', None)
        plus = request.args.get('plus', None)
        new_user_is_client = request.args.get('is_client', None)
    elif request.method == 'POST':
        admin = request.json.get('admin', None)
        client = request.json.get('client', None)
        userid = request.json.get('userid', None)
        username = request.json.get('username', None)
        plus = request.json.get('plus', None)
        new_user_is_client = request.json.get('is_client', 'false')
    
    is_admin = False
    is_client = False
    if admin is not None and admin != "":
        admin_check = await ChatGPTServer.check_admin(user=admin)
        if admin_check['status'] == 'error':
            return admin_check, 400 #Return Error Message if Admin is Invalid
        else:
            is_admin = True
    
    if client is not None and client != "":
        client_check = await ChatGPTServer.check_client(user=client)
        if client_check['status'] == 'error':
            return client_check, 400 #Return Error Message if Client is Invalid
        else:
            is_client = True
    
    if not is_admin and not is_client:
        response['status'] = 'error'
        response['message'] = 'No valid Admin or Client API Key provided'
        return jsonify(response), 400
    else:
        if is_client:
            if new_user_is_client == "true":
                response['status'] = 'error'
                response['message'] = 'Clients cannot create new clients'
                return jsonify(response), 400
    
    if plus == "true":
        plus = True
    elif plus == "false":
        plus = False

    if new_user_is_client == "true":
        new_user_is_client = True
    elif new_user_is_client == "false":
        new_user_is_client = False
    
    status, message, key = await ChatGPTServer.add_user(client=client, userid=userid, username=username, plus=plus, is_client=new_user_is_client)
    response['status'] = status
    response['message'] = message
    response['api_key'] = key
    if status == 'error':
        return jsonify(response), 422
    else:
        return jsonify(response), 200    

#Redirect Root to Browser
@app.route("/", methods=["GET"])
def root():
    return redirect(url_for('chat'))

# Load Browser Favorite Icon
@app.route('/android-chrome-192x192.png', methods=["GET"])
def android_chrome_192():
    return url_for('static', filename='image/android-chrome-192x192.png')

@app.route('/android-chrome-512x512.png', methods=["GET"])
def android_chrome_512():
    return url_for('static', filename='image/android-chrome-512x512.png')

@app.route('/apple-touch-icon.png', methods=["GET"])
def apple_touch_icon():
    return url_for('static', filename='image/apple-touch-icon.png')

@app.route('/favicon.ico', methods=["GET"])
def favicon():
    return url_for('static', filename='image/favicon.ico')

@app.route('/favicon-16x16.png', methods=["GET"])
def favicon_16():
    return url_for('static', filename='image/favicon-16x16.png')

@app.route('/favicon-32x32.png', methods=["GET"])
def favicon_32():
    return url_for('static', filename='image/favicon-32x32.png')