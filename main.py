from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Environment Variables
TOKEN = os.getenv("TOKEN")               # Instagram Page Access Token
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") # Webhook verify token
AI_KEY = os.getenv("AI_KEY")             # Groq API Key


# ---------- AI FUNCTION ----------
def ask_ai(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a smart assistant answering customers clearly."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post(url, json=data, headers=headers)
        out = res.json()
        return out["choices"][0]["message"]["content"]
    except Exception as e:
        print("AI ERROR:", e)
        return "Sorry, I couldn't process your message."


# ---------- VERIFY WEBHOOK ----------
@app.route("/", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403


# ---------- RECEIVE INSTAGRAM MESSAGE ----------
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("WEBHOOK RECEIVED:", data)

        # Instagram uses "changes"
        change = data["entry"][0]["changes"][0]
        value = change["value"]

        if "messages" in value:
            msg = value["messages"][0]["text"]
            sender = value["messages"][0]["from"]["id"]

            reply = ask_ai(msg)
            send_message(sender, reply)

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200


# ---------- SEND MESSAGE BACK TO INSTAGRAM ----------
def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={TOKEN}"

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    try:
        requests.post(url, json=payload)
        print("REPLY SENT:", text)
    except Exception as e:
        print("SEND ERROR:", e)



# ---------- RUN SERVER ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
