import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# === Replace with your Bot Token from @BotFather ===
TOKEN = '7918229131:AAGHphzn3CCrnkD0xJ5ztBkBpOeTJbk5L9A'
bot = telebot.TeleBot(TOKEN)

# === File to store user data ===
DATA_FILE = 'users.json'

# === Load or initialize data ===
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
else:
    users = {}

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = str(message.from_user.id)
    args = message.text.split()

    if user_id not in users:
        users[user_id] = {
            'balance': 0,
            'referrer': None,
            'claimed': False
        }
        # Handle referral
        if len(args) > 1:
            referrer = args[1]
            if referrer != user_id and referrer in users:
                users[user_id]['referrer'] = referrer
                users[referrer]['balance'] += 1  # Give 1 point to referrer

    save_data()

    bot.send_message(message.chat.id,
        f"👋 Welcome to the Giveaway Bot!\n\n"
        f"💰 Your balance: {users[user_id]['balance']} points\n"
        f"🎁 Press the button below to claim your reward.")

    show_claim_button(message.chat.id)

def show_claim_button(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Join & Verify", callback_data="verify"))
    bot.send_message(chat_id, "Follow the instructions:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_user(call):
    user_id = str(call.from_user.id)

    if users[user_id]['claimed']:
        bot.answer_callback_query(call.id, "⚠️ You’ve already claimed the reward.")
    else:
        users[user_id]['balance'] += 10  # Initial reward
        users[user_id]['claimed'] = True
        save_data()
        bot.answer_callback_query(call.id, "🎉 Verified! You received 10 points.")
        bot.send_message(call.message.chat.id, f"💰 Your new balance: {users[user_id]['balance']} points")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    user_id = str(message.from_user.id)
    if user_id in users:
        bot.send_message(message.chat.id, f"💰 Your balance: {users[user_id]['balance']} points")
    else:
        bot.send_message(message.chat.id, "❗ Please start the bot using /start.")

@bot.message_handler(commands=['refer'])
def referral_link(message):
    user_id = str(message.from_user.id)
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    bot.send_message(message.chat.id, f"🔗 Your referral link:\n{link}")

print("Bot is running...")
bot.polling()