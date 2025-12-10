from instagrapi import Client
from dotenv import load_dotenv
import time
import requests
import os

load_dotenv()

AI_KEY = os.getenv("AI_KEY")  # مفتاح Groq
USERNAME = os.getenv("IG_USER")
PASSWORD = os.getenv("IG_PASS")

cl = Client()
cl.login(USERNAME, PASSWORD)

def ask_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": text}]
    }
    res = requests.post(url, json=data, headers=headers)
    return res.json()["choices"][0]["message"]["content"]

def run_bot():
    last = {}
    while True:
        inbox = cl.direct_threads()
        for thread in inbox:
            user = thread.user_ids[0]
            msg = thread.messages[0]

            if msg.id != last.get(user):
                if msg.text:
                    reply = ask_ai(msg.text)
                    cl.direct_send(reply, user)
                    print("رد على:", msg.text)
                
                last[user] = msg.id
        
        time.sleep(3)


run_bot()
