from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# CORS allow karta hai taaki aapka GitHub Pages wala frontend isse baat kar sake
CORS(app)

# API Key hum server ke environment se lenge (Secure tarika)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route('/', methods=['GET'])
def home():
    return "JARVIS Core Backend is Online and Running."

@app.route('/chat', methods=['POST'])
def chat():
    # Frontend se aaya hua message
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if not GEMINI_API_KEY:
        return jsonify({"error": "API Key is missing on the server"}), 500

    # Gemini API ko request bhejna
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # System Prompt (JARVIS ka character)
    system_prompt = "You are JARVIS, a highly advanced and polite AI assistant created by Krishna. Give short, direct, and conversational answers."
    
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt} User says: {user_message}"}]}]
    }

    try:
        # Secure server-to-server call
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        # Gemini ka answer extract karna
        jarvis_reply = response_data['candidates'][0]['content']['parts'][0]['text']
        
        # Wapas frontend (app) ko answer bhejna
        return jsonify({"reply": jarvis_reply})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Server ko run karna
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
