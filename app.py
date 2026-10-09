import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


@app.get("/")
def home():
    return jsonify({
        "service": "JARVIS AI Backend",
        "status": "online",
        "chat_endpoint": "/chat"
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok", "api_key_configured": bool(GEMINI_API_KEY)})


def extract_message(data):
    # Frontend currently sends {"message": "..."}.
    message = data.get("message")
    if isinstance(message, str) and message.strip():
        return message.strip()

    # Also accept OpenAI-style chat completion payloads.
    messages = data.get("messages", [])
    if isinstance(messages, list):
        for item in reversed(messages):
            if isinstance(item, dict) and item.get("role") == "user":
                content = item.get("content", "")
                if isinstance(content, str) and content.strip():
                    return content.strip()
    return ""


@app.route("/chat", methods=["POST", "OPTIONS"])
@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    user_message = extract_message(data)
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if not GEMINI_API_KEY:
        return jsonify({
            "error": "GEMINI_API_KEY is not configured in the hosting environment."
        }), 503

    payload = {
        "system_instruction": {
            "parts": [{
                "text": (
                    "You are JARVIS, a helpful personal AI assistant created by Krishna. "
                    "Reply naturally and conversationally. Use Hindi or Hinglish when the "
                    "user does. Keep answers concise unless more detail is requested."
                )
            }]
        },
        "contents": [{
            "role": "user",
            "parts": [{"text": user_message}]
        }],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}
    }

    try:
        response = requests.post(
            GEMINI_URL.format(model=GEMINI_MODEL),
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=40
        )
        if not response.ok:
            app.logger.error("Gemini API returned %s: %s", response.status_code, response.text[:1000])
            return jsonify({
                "error": "Gemini API request failed.",
                "details": response.json().get("error", {}).get("message", "Upstream API error")
                    if response.headers.get("content-type", "").startswith("application/json")
                    else "Upstream API error"
            }), 502

        result = response.json()
        candidates = result.get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        reply = " ".join(part.get("text", "") for part in parts if part.get("text"))
        if not reply:
            return jsonify({"error": "Gemini returned an empty response."}), 502

        # Keep the existing frontend contract and support OpenAI-style clients.
        return jsonify({
            "reply": reply,
            "choices": [{"message": {"role": "assistant", "content": reply}}]
        })
    except requests.Timeout:
        return jsonify({"error": "Gemini request timed out. Please try again."}), 504
    except requests.RequestException:
        app.logger.exception("Unable to reach Gemini API")
        return jsonify({"error": "Unable to reach Gemini API."}), 502
    except Exception:
        app.logger.exception("Unexpected JARVIS backend error")
        return jsonify({"error": "Unexpected backend error."}), 500


@app.post("/telegram/webhook")
def telegram_webhook():
    """Receive Telegram updates and forward text messages to the existing JARVIS chat API."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return jsonify({"error": "TELEGRAM_BOT_TOKEN is not configured"}), 503

    expected_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    supplied_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if expected_secret and supplied_secret != expected_secret:
        return jsonify({"error": "Unauthorized"}), 403

    update = request.get_json(silent=True) or {}
    message = update.get("message") or update.get("edited_message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return jsonify({"ok": True})

    # Basic commands
    if text.startswith("/start"):
        reply = "JARVIS online, Krishna. Mujhe message bhejo aur main jawab dunga. 🤖"
    elif text.startswith("/help"):
        reply = "Commands: /start, /help. Normal message bhejkar JARVIS se baat karo."
    else:
        try:
            base_url = request.url_root.rstrip("/")
            ai_response = requests.post(
                base_url + "/chat",
                json={"message": text},
                timeout=45
            )
            data = ai_response.json() if ai_response.content else {}
            if ai_response.ok and data.get("reply"):
                reply = str(data["reply"])
            else:
                reply = "JARVIS AI abhi reply nahi kar pa raha. Thodi der baad try karo."
                app.logger.error("Telegram chat forwarding failed: HTTP %s", ai_response.status_code)
        except requests.RequestException:
            app.logger.exception("Could not forward Telegram message to JARVIS chat")
            reply = "JARVIS backend se connection fail hua. Please thodi der baad try karo."

    try:
        telegram_response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": reply[:4000]},
            timeout=15
        )
        if not telegram_response.ok:
            app.logger.error("Telegram sendMessage failed: %s", telegram_response.text[:500])
            return jsonify({"error": "Telegram could not send the reply"}), 502
    except requests.RequestException:
        app.logger.exception("Could not send Telegram reply")
        return jsonify({"error": "Telegram API unavailable"}), 502

    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
