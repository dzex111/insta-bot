from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TOKEN = os.getenv("TOKEN")               # Instagram Token
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") # Webhook Verify Token
AI_KEY = os.getenv("AI_KEY")             # Groq AI Key

def ask_ai(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are smart assistant for a company. Reply clearly."},
            {"role": "user", "content": prompt}
        ]
    }
    res = requests.post(url, json=data, headers=headers)
    return res.json()["choices"][0]["message"]["content"]


# -----------------------------
# VERIFY WEBHOOK
# -----------------------------
@app.route('/', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


# -----------------------------
# RECEIVE & RESPOND
# -----------------------------
@app.route('/', methods=['POST'])
def webhook():
    data = request.json

    try:
        msg = data["entry"][0]["messaging"][0]["message"]["text"]
        sender = data["entry"][0]["messaging"][0]["sender"]["id"]

        reply = ask_ai(msg)

        send_message(sender, reply)

    except Exception as e:
        print("Error:", e)

    return "ok", 200


def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
