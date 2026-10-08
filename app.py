from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route('/', methods=['GET'])
def home():
    return "JARVIS OpenAI-Compatible Backend is Online."

# App ko lagna chahiye ki wo OpenAI se baat kar raha hai
@app.route('/v1/chat/completions', methods=['POST'])
def chat():
    data = request.json
    
    # App se message nikalna (OpenAI format se)
    try:
        messages = data.get("messages", [])
        user_message = messages[-1].get("content", "")
    except:
        user_message = ""

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if not GEMINI_API_KEY:
        return jsonify({"error": "API Key missing"}), 500

    # Gemini API ko request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    system_prompt = "You are JARVIS, a highly advanced AI assistant created by Krishna. Give short, direct, and conversational answers."
    
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt} User says: {user_message}"}]}]
    }

    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        jarvis_reply = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # Wapas App ko OpenAI format mein reply bhejna
        return jsonify({
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": jarvis_reply
                }
            }]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
