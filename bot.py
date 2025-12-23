import telebot
import requests
import re
import time
import os
from flask import Flask
from threading import Thread

# --- Flask Server (Render এর জন্য জরুরি) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

# --- কনফিগারেশন ---
API_TOKEN = '8247047956:AAGpILfNSVNt-62GZIqF80ZNF1eXUbikX9k'
ADMIN_ID = 8220394592
OTP_GROUP_ID = -1003635642681 

bot = telebot.TeleBot(API_TOKEN)

# সরাসরি রিকোয়েস্ট মেথড (টারমাক্স বা রেন্ডার সব জায়গায় চলবে)
def get_mnit_number(cookie, target_range):
    url = "https://v2.mnitnetwork.com/dashboard/getnum"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie.encode('ascii', 'ignore').decode('ascii'),
        "Referer": url
    }
    payload = {"range": target_range, "action": "get_number"}
    
    try:
        session = requests.Session()
        res = session.post(url, headers=headers, data=payload, timeout=15)
        clean_range = target_range.replace('X', '')
        find_num = re.findall(rf'{clean_range}\d{{4,10}}', res.text)
        return find_num[0] if find_num else None
    except:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "বটটি Render-এ সফলভাবে চালু হয়েছে! কমান্ড দিয়ে কন্ট্রোল করুন।")

# বটের বাকি এডমিন কমান্ডগুলো এখানে যুক্ত করুন...

if __name__ == "__main__":
    # সার্ভার এবং বট একসাথে চালু করা
    t = Thread(target=run)
    t.start()
    print("🚀 Render Bot Started...")
    bot.infinity_polling()
    