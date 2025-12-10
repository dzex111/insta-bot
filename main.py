from instagrapi import Client
from dotenv import load_dotenv
import time
import os
import requests

load_dotenv()

AI_KEY = os.getenv("AI_KEY")
IG_USER = os.getenv("IG_USER")
IG_PASS = os.getenv("IG_PASS")

# ---------------- LOGIN ----------------
cl = Client()

try:
    cl.login(IG_USER, IG_PASS)
    print("✔ Logged into Instagram successfully.")
except Exception as e:
    print("❌ Login failed:", e)
    exit()


# ---------------- AI REPLY ----------------
def ask_ai(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a smart helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post(url, json=data, headers=headers)
        response = res.json()["choices"][0]["message"]["content"]
        return response
    except Exception as e:
        print("AI ERROR:", e)
        return "Sorry, something went wrong."


# ---------------- BOT LOOP ----------------
def run_bot():
    print("🤖 Bot is running and watching messages…")
    last_seen = {}

    while True:
        try:
            inbox = cl.direct_threads()

            for thread in inbox:
                uid = thread.user_ids[0]
                msg = thread.messages[0]

                if msg.id != last_seen.get(uid):
                    if msg.text:
                        print(f"📩 New message from {uid}: {msg.text}")
                        reply = ask_ai(msg.text)
                        cl.direct_send(reply, uid)
                        print("📤 Sent reply:", reply)

                    last_seen[uid] = msg.id

            time.sleep(3)

        except Exception as e:
            print("BOT LOOP ERROR:", e)
            time.sleep(5)


if __name__ == "__main__":
    run_bot()
