#IMPORT BUILT-IN LIBRARIES
import asyncio

#IMPORT THIRD-PARTY LIBRARIES
from flask import Flask
from flask import jsonify
from flask import request
from waitress import serve

#IMPORT FROM PROJECT SETTINGS
from chatgpt import ChatGPT
from settings import API_HOST, API_PORT, OPENAI_DEFAULT_TEMPERATURE, OPENAI_DEFAULT_PROMPT, OPENAI_DEFAULT_PROMPT

#SETUP FLASK APP
app = Flask(__name__)

#SETUP ROUTES
@app.route("/chat", methods=["GET", "POST"])
async def chat():

    if request.method == "GET":
        prompt = request.args.get("prompt", OPENAI_DEFAULT_PROMPT)
        temperature = request.args.get("temperature", OPENAI_DEFAULT_TEMPERATURE)
    elif request.method == "POST":
        prompt = request.json.get("prompt", OPENAI_DEFAULT_PROMPT)
        temperature = request.json.get("temperature", OPENAI_DEFAULT_TEMPERATURE)
    
    try:
        response = await ChatGPT.ask(
            prompt=prompt,
            temperature=temperature
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    
    return jsonify(response), 200

def main():
    print(f"ChatGPT API is loading on {API_HOST}:{API_PORT}...")
    serve(app, host=API_HOST, port=int(API_PORT))    

if __name__ == "__main__":
    asyncio.run(main())
