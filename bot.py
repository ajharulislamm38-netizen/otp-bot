import telebot
from telebot import types
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

# ================ কনফিগারেশন ================
API_TOKEN = '8247047956:AAGpILfNSVNt-62GZIqF80ZNF1eXUbikX9k'
ADMIN_ID = 8220394592  # আপনার আইডি
OTP_GROUP_ID = -1003635642681 

bot = telebot.TeleBot(API_TOKEN)

# ডেটা স্টোর করার জন্য (ইন-মেমোরি)
user_data = {"cookie": "", "range": ""}

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🍪 Update Cookie", "🔢 Set Range")
        markup.add("🎯 Get Number Now")
        bot.send_message(message.chat.id, "🛠 **Admin Panel Active**\nনিচের বাটনগুলো ব্যবহার করুন:", reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ আপনি এই বটের এডমিন নন।")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_controls(message):
    if message.text == "🍪 Update Cookie":
        msg = bot.send_message(message.chat.id, "আপনার নতুন Cookie পেস্ট করুন:")
        bot.register_next_step_handler(msg, update_cookie)
    elif message.text == "🔢 Set Range":
        msg = bot.send_message(message.chat.id, "নতুন রেঞ্জ দিন (যেমন: 232739XXX):")
        bot.register_next_step_handler(msg, update_range)
    elif message.text == "🎯 Get Number Now":
        process_number_request(message.chat.id)

def update_cookie(message):
    user_data["cookie"] = message.text.encode('ascii', 'ignore').decode('ascii').strip()
    bot.send_message(message.chat.id, "✅ Cookie আপডেট সফল!")

def update_range(message):
    user_data["range"] = message.text.strip()
    bot.send_message(message.chat.id, f"✅ রেঞ্জ `{message.text}` সেট হয়েছে।")

def process_number_request(chat_id):
    cookie = user_data["cookie"]
    target_range = user_data["range"]

    if not cookie or not target_range:
        bot.send_message(chat_id, "❌ আগে কুকি এবং রেঞ্জ সেট করুন!")
        return

    bot.send_message(chat_id, "⏳ নাম্বার খোঁজা হচ্ছে...")
    
    url = "https://v2.mnitnetwork.com/dashboard/getnum"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie,
        "Referer": url
    }
    payload = {"range": target_range, "action": "get_number"}

    try:
        session = requests.Session()
        res = session.post(url, headers=headers, data=payload, timeout=15)
        
        clean_range = target_range.replace('X', '')
        find_num = re.findall(rf'{clean_range}\d{{4,10}}', res.text)

        if find_num:
            number = find_num[0]
            bot.send_message(chat_id, f"✅ নাম্বার: `{number}`\n⏳ ওটিপি চেক হচ্ছে...", parse_mode="Markdown")
            
            # ওটিপি লুপ
            for _ in range(20):
                time.sleep(12)
                check_res = session.get(url, headers=headers)
                otp = re.search(fr'{number}.*?\b(\d{{4,6}})\b', check_res.text, re.DOTALL)
                if otp:
                    otp_code = otp.group(1)
                    msg = f"🎉 **OTP Received!**\n📞 `{number}`\n🔑 `{otp_code}`"
                    bot.send_message(chat_id, msg, parse_mode="Markdown")
                    bot.send_message(OTP_GROUP_ID, msg, parse_mode="Markdown")
                    return
            bot.send_message(chat_id, "❌ ওটিপি আসেনি।")
        else:
            bot.send_message(chat_id, "❌ নাম্বার পাওয়া যায়নি।")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ এরর: {str(e)}")

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
    
