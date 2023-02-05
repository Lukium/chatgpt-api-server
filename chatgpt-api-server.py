#IMPORT BUILT-IN LIBRARIES
import json
import asyncio
from datetime import datetime

#IMPORT THIRD-PARTY LIBRARIES
from flask import Flask
from flask import jsonify
from flask import request
from waitress import serve
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension

#IMPORT FROM PROJECT SETTINGS
from chatgpt import ChatGPT
from settings import API_HOST, API_PORT, OPENAI_DEFAULT_TEMPERATURE, OPENAI_DEFAULT_PROMPT, OPENAI_DEFAULT_PROMPT
from html_blocks import HTML_HEADER, HTML_FOOTER

#SETUP FLASK APP
app = Flask(__name__)

#SETUP ROUTES
@app.route("/chat", methods=["GET", "POST"])
async def chat():

    if request.method == "GET":        
        prompt = request.args.get("prompt", OPENAI_DEFAULT_PROMPT)
        temperature = float(request.args.get("temperature", OPENAI_DEFAULT_TEMPERATURE))
        browser_reply = request.args.get("browser_reply", "false")
    elif request.method == "POST":
        prompt = request.json.get("prompt", OPENAI_DEFAULT_PROMPT)
        temperature = float(request.json.get("temperature", OPENAI_DEFAULT_TEMPERATURE))
        browser_reply = request.json.get("browser_reply", "false")

    start_time = datetime.now() #Start counting time
    
    try:
        response = await ChatGPT.ask(
            prompt=prompt,
            temperature=temperature
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    
    end_time = datetime.now() #Stop counting time
    response_time = str(round((end_time - start_time).total_seconds(), 2)) #Calculate time difference
    
    response['temperature'] = temperature #Add temperature to response object
    response['response_time'] = response_time #Add response time to response object
    response['original_prompt'] = prompt #Add prompt to response object
    
    if browser_reply == "true":
        reply = response.choices[0].text.rstrip("<|im_end|>")

        md = markdown.Markdown(extensions=['fenced_code', CodeHiliteExtension(linenums=True, guess_lang=True, use_pygmnet=True, css_class='highlight')])        
        html = md.convert(reply)
        html = HTML_HEADER + html + HTML_FOOTER

        return html, 200
    
    return json.loads(str(response)), 200

def main():
    print(f"ChatGPT API is loading on {API_HOST}:{API_PORT}...")
    serve(app, host=API_HOST, port=int(API_PORT))    

if __name__ == "__main__":
    asyncio.run(main())
