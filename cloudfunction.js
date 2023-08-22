import os
import openai
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


# Setup OpenAI API key from environment variable or secret manager here
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Read resume details once when the function is initialized
with open('jadens_resume.txt', 'r') as f:
    resume_details = f.read()

def chatbot_response(request):
    # For handling the CORS preflight request
    if request.method == "OPTIONS":
        response = make_response("", 204)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response
    # Existing POST logic
    elif request.method == "POST":
        data = request.get_json(silent=True)
        
        # If messages aren't present or if it's an empty array, add the system and user message
        if not data.get("messages"):
            return jsonify(error="No messages provided"), 400

        # Prepend the system message to the beginning of the messages list if it's not already present
        if not (data["messages"][0]["role"] == "system" and "Jaden-Bot" in data["messages"][0]["content"]):
            system_message = {
                "role": "system",
                "content": f"You are Jaden-Bot, a chatbot designed to answer questions related to Jaden's resume:\n{resume_details}"
            }
            data["messages"].insert(0, system_message)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=data["messages"],  # Use the messages directly from the request
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract the chatbot's response from the API result
        bot_response = response.choices[0].message["content"]

        response = make_response(jsonify(bot_response), 200)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    # Default response for other HTTP methods
    else:
        response = make_response(jsonify(error="Only POST requests are allowed"), 405)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response