#IMPORT BUILT-IN LIBRARIES
import asyncio

#IMPORT THIRD-PARTY LIBRARIES
from flask import Flask
from flask import jsonify
from flask import request
from waitress import serve

#IMPORT FROM PROJECT SETTINGS
from chatgpt import ChatGPT
from settings import API_HOST, API_PORT

#SETUP FLASK APP
app = Flask(__name__)

#SETUP ROUTES
@app.route("/chat", methods=["GET"])
async def chat():

    prompt = request.args.get("prompt", None)
    if prompt is None:
        return jsonify({"error": "Request did not include a prompt"}), 400
    
    try:
        response = await ChatGPT.ask(
            prompt=prompt
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    
    return jsonify(response), 200

def main():
    print(f"ChatGPT API is loading on {API_HOST}:{API_PORT}...")
    serve(app, host=API_HOST, port=int(API_PORT))    

if __name__ == "__main__":
    asyncio.run(main())