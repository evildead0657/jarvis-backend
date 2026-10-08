# 🧠 JARVIS AI - Backend Proxy Server

This repository contains the secure Python backend for the JARVIS Personal AI Assistant. It acts as a middleware proxy server to handle communication between the frontend client app and the Google Gemini AI, ensuring that secret API keys are never exposed to the public internet.

## 🚀 Tech Stack
* **Language:** Python 3
* **Framework:** Flask (Web Server)
* **AI Integration:** Google Gemini 1.5 Flash API
* **Security:** Flask-CORS (Cross-Origin Resource Sharing)
* **Deployment:** Render / Heroku

## ⚙️ Core Features
* **Secure Key Management:** Uses Environment Variables to protect API keys. No hardcoded secrets.
* **CORS Enabled:** Fully configured to seamlessly accept voice-to-text requests from the frontend app.
* **Lightweight & Fast:** Minimal dependencies for fast boot times and instant AI responses.

## 📡 API Reference

### 1. Health Check
* **Endpoint:** `/`
* **Method:** `GET`
* **Description:** Used to verify if the JARVIS core backend is online and running.

### 2. Chat Completions
* **Endpoint:** `/chat`
* **Method:** `POST`
* **Payload:** `{"message": "User's voice command text"}`
* **Description:** Processes the user's prompt via the Gemini LLM and returns the intelligent response.

## 🔒 Security Note
Do not hardcode the `GEMINI_API_KEY` in the source code. Always configure it in the Environment Variables of your hosting provider (like Render).

---
*Developed by Krishna for the JARVIS AI Project.*
