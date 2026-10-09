# JARVIS Krishna — Backend

Flask API for the JARVIS web interface and Telegram bot.

## Endpoints

- `GET /` — service status
- `GET /health` — backend health and whether the Gemini key is configured
- `POST /chat` — send `{"message":"Hello"}`, receive `{"reply":"..."}`
- `POST /v1/chat/completions` — OpenAI-style compatibility route
- `POST /telegram/webhook` — Telegram bot webhook

## Render environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes for AI replies | Google AI Studio API key |
| `GEMINI_MODEL` | No | Defaults to `gemini-2.5-flash` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot only | Token from @BotFather |
| `TELEGRAM_WEBHOOK_SECRET` | Recommended for Telegram | Validates webhook requests |

Never put API keys or bot tokens in frontend HTML or commit them to GitHub.

## Connect Telegram

After setting the Telegram environment variables and redeploying, set the webhook URL using Telegram's Bot API:

`https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://YOUR-RENDER-SERVICE/telegram/webhook&secret_token=<WEBHOOK_SECRET>`

Replace placeholders locally. Do not publish the completed URL because it contains the bot token.

## Test

Open `/health`. Expected response includes `"status":"ok"` and `"api_key_configured":true`. Then send a POST request to `/chat` with a JSON `message` field.

Telegram currently supports text messages and text replies. Voice-note transcription and audio replies are not implemented yet.
