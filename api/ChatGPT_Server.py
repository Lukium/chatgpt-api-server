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

#IMPORT SETTINGS
import settings.Settings as Settings

#IMPORT HELPERS
from helpers.APIUsers import add #For adding users to the API


#SETUP FLASK APP
app = Flask(__name__)
app.config['SECRET_KEY'] = Settings.API_APP_SECRET
Bootstrap(app)

ChatGPTServer = asyncio.run(ChatGPTServer.create())
    
#SETUP ROUTES
@app.route("/api/chat", methods=["GET", "POST"])
async def api_direct():
    response: dict = {}

    if request.method == "GET":
        prompt = request.args.get("prompt", Settings.API_DEFAULT_PROMPT)
        user = request.args.get("user", None)
        plus = request.args.get("plus", "false")
        reply_only = request.args.get("reply_only", "false")
        pretty = request.args.get("pretty", "false")
        access_token = request.args.get("access_token", None)
        user_plus = request.args.get("user_plus", "false")
    elif request.method == "POST":
        prompt = request.json.get("prompt", Settings.API_DEFAULT_PROMPT)
        user = request.json.get("user", None)
        plus = request.json.get("plus", "false")
        reply_only = request.json.get("reply_only", "false")
        pretty = request.json.get("pretty", "false")
        access_token = request.json.get("access_token", None)
        user_plus = request.json.get("user_plus", "false")
    
    user_check = await ChatGPTServer.check_user(user=user)
    if user_check['status'] == 'error':
        return user_check, 400 #Return Error Message if User is Invalid
    
    if access_token != "" and access_token is not None:
        response: dict = await ChatGPTServer.process_chagpt_request(
            prompt=prompt,
            type='user',
            access_token=access_token,
            user_plus=user_plus
            )
    else:
        response: dict = await ChatGPTServer.process_chagpt_request(
            prompt=prompt,
            plus=plus
            )
            
    if reply_only == "true":
        response = await ChatGPTServer.process_reply_only(
            response=response,
            pretty=pretty
            )
        
    return response, 200


@app.route("/chat", methods=["GET", "POST"])
async def chat():
    form = FormChatGPT()
    user = request.args.get("user", None)
    access_token = request.args.get("access_token", None)
    if user is not None:
        form.api_key.data = user
    if access_token is not None:
        form.access_token.data = access_token
    message = f'Please be patient while your request is processed...'
    message2 = f'The time required to process is proportional to the length of the reply.'
    if form.validate_on_submit():
        #Perform User Check
        user_check = await ChatGPTServer.check_user(user=user)
        if user_check['status'] == 'error':
            return user_check, 400 #Return Error Message if User is Invalid        
        
        if form.access_token.data != "":
            response: dict = await ChatGPTServer.process_chagpt_request(
                prompt=form.prompt.data,
                type='user',
                access_token=form.access_token.data,
                user_plus=form.user_plus.data
                )
        else:
            response: dict = await ChatGPTServer.process_chagpt_request(
                prompt=form.prompt.data,
                plus=form.plus.data
                )
        
        if form.reply_only.data == "true":
            response = await ChatGPTServer.process_reply_only(
                response=response,
                pretty=form.pretty.data
                )
            
        return response, 200
    return render_template("index.html", form=form, message=message, message2=message2)
    
@app.route("/api/access-token", methods=["GET", "POST"])
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

@app.route("/access-token", methods=["GET", "POST"])
async def access_token():
    form = FormAccessToken()
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

    return render_template("access-token.html", form=form, message=message)

@app.route("/admin/add-user", methods=["GET", "POST"])
def add_user():
    response: dict = {}
    admin_api_key = request.args.get("admin", None)
    if admin_api_key is None:
        response['status'] = 'error'
        response['message'] = 'No API Key provided'
        return jsonify(response), 400
    elif admin_api_key != Settings.API_ADMIN_KEY:
        response['status'] = 'error'
        response['message'] = 'Invalid API Key'
        return jsonify(response), 400
    else:
        form = FormAddUser()
        if form.validate_on_submit():
            userid = form.userid.data
            username = form.username.data
            plus = form.plus.data
            if plus == "true":
                plus = True
            elif plus == "false":
                plus = False
            status, message, key = add(userid=userid, username=username, plus=plus)
            response['status'] = status
            response['message'] = message
            response['api_key'] = key
            if status == 'error':
                return jsonify(response), 422
            else:
                return jsonify(response), 200
        return render_template("admin/add-user.html", form=form)

#Redirect Root to Browser
@app.route("/", methods=["GET"])
def root():
    return redirect(url_for('chat'))

# Load Browser Favorite Icon
@app.route('/android-chrome-192x192.png')
def android_chrome_192():
    return url_for('static', filename='image/android-chrome-192x192.png')

@app.route('/android-chrome-512x512.png')
def android_chrome_512():
    return url_for('static', filename='image/android-chrome-512x512.png')

@app.route('/apple-touch-icon.png')
def apple_touch_icon():
    return url_for('static', filename='image/apple-touch-icon.png')

@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='image/favicon.ico')

@app.route('/favicon-16x16.png')
def favicon_16():
    return url_for('static', filename='image/favicon-16x16.png')

@app.route('/favicon-32x32.png')
def favicon_32():
    return url_for('static', filename='image/favicon-32x32.png')