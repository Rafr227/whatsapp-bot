
import requests
import time
import threading
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# API URLs (Unofficial)
LOGIN_URL = "https://quotex.io/api/login"
TRADE_URL = "https://quotex.io/api/trade"
BALANCE_URL = "https://quotex.io/api/balance"

# User Credentials (Replace with real ones)
EMAIL = "user@example.com"
PASSWORD = "yourpassword"
TELEGRAM_BOT_TOKEN = "7868632924:AAHV_ext2ZWQqhlAzGlZDBpgw0JLfaUL5YY"
CHAT_ID = "your_chat_id"

# Global Variables
session = None
token = None
trading = False
direction = "call"

# Telegram Message
async def send_telegram_message(text):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

# Login Function
def login():
    global session, token
    session = requests.Session()
    payload = {"email": EMAIL, "password": PASSWORD}
    response = session.post(LOGIN_URL, json=payload)
    if response.status_code == 200 and "token" in response.json():
        token = response.json()["token"]
        return True
    return False

# Trade Function
def place_trade():
    global session, token, direction
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "asset": "EUR/USD",
        "direction": direction,
        "amount": 1,
        "duration": 1
    }
    response = session.post(TRADE_URL, json=payload, headers=headers)
    if response.status_code == 200:
        msg = f"✅ Trade Placed: {direction.upper()} EUR/USD for $1"
    else:
        msg = "❌ Trade Failed"
    asyncio.run(send_telegram_message(msg))

# Balance Check
def check_balance():
    global session, token
    headers = {"Authorization": f"Bearer {token}"}
    response = session.get(BALANCE_URL, headers=headers)
    if response.status_code == 200:
        balance = response.json().get("balance", "Unknown")
        return f"💰 Balance: ${balance}"
    return "❌ Failed to get balance"

# Trade Loop
def trade_loop():
    while trading:
        place_trade()
        time.sleep(60)

# Telegram Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global trading
    if login():
        trading = True
        threading.Thread(target=trade_loop).start()
        await update.message.reply_text("✅ Trading Started!")
    else:
        await update.message.reply_text("❌ Login Failed")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global trading
    trading = False
    await update.message.reply_text("⛔ Trading Stopped!")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global direction
    direction = "call"
    await update.message.reply_text("📈 Direction set to BUY")

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global direction
    direction = "put"
    await update.message.reply_text("📉 Direction set to SELL")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = check_balance()
    await update.message.reply_text(bal)

# Main Bot Setup
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("sell", sell))
    app.add_handler(CommandHandler("balance", balance))
    app.run_polling()

if __name__ == "__main__":
    main()
