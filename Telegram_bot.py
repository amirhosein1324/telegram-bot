import logging
import requests
from bs4 import BeautifulSoup
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import json
import random
import os
import asyncio
from datetime import datetime

BOT_TOKEN = " REPLACE IT WITH YOURE TELEGRAM BOT CODE"
USER_FILE = 'users.json'
CHANNEL_ID = "YOURE TELEGRAM CHANNEL ID"  

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

def add_user(user_id):
    users = load_users()
    users[str(user_id)] = datetime.now().isoformat()
    save_users(users)

def remove_user(user_id):
    users = load_users()
    if str(user_id) in users:
        del users[str(user_id)]
        save_users(users)

async def send_channel_update(context: ContextTypes.DEFAULT_TYPE):
    try:
        now = datetime.now()
        btc_data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
        
        message = (
            f"🔄 Channel Update\n\n"
            f"📅 Date: {now.strftime('%Y-%m-%d')}\n"
            f"⏰ Time: {now.strftime('%H:%M:%S')}\n"
            "✅ Updated"
        )
        
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=message
        )
        logger.info(f"Sent update to channel {CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Channel update failed: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    add_user(user.id)
    welcome_msg = (
        f"Hi {user.mention_html()}! 👋\n\n"
        "I'm a bot that can:\n"
        "- Show BTC price (/btc_price)\n"
        "- Show news (/news)\n"
        "- Check crypto prices (e.g., /price_bitcoin)\n"
        "- you can check any crypto price with:(/price cryptoname)\n "
        "- help command (/help)\n\n"
        "You'll occasionally receive random messages from me. "
        "Use /optout if you don't want these."
    )
    await update.message.reply_text(
        welcome_msg,
        parse_mode='HTML',
        reply_markup=ForceReply(selective=True)
    )

async def optout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    remove_user(user_id)
    await update.message.reply_text(
        "You've been removed from messaging list. Use /start to re-enable."
    )

async def get_btc_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_user(update.effective_user.id)
    try:
        response = requests.get("https://blockchain.info/ticker").json()
        await update.message.reply_text(f"💰 BTC price now: {response['USD']['buy']}$")
    except Exception as e:
        await update.message.reply_text("⚠️ Couldn't fetch BTC price")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📋 Available commands:\n\n"
        "/start - Welcome message\n"
        "/help - This message\n"
        "/btc_price - Bitcoin price\n"
        "/news - Latest sports news\n"
        "/price_<coin> - Crypto price (e.g. /price_bitcoin)\n"
        "/optout - Stop random messages\n\n"
        "Channel updates sent automatically every 5 minutes"
    )
    await update.message.reply_text(help_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_user(update.effective_user.id)
    await update.message.reply_text(update.message.text)

def get_news() -> list:
    news_articles = []
    try:
        response = requests.get("https://www.varzesh3.com/", timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all("div", {"class": "news-main-list"})
        for div in divs[:10]:
            for link in div.find_all("a"):
                if "news" in link["href"]:
                    news_articles.append(link["href"])
                    if len(news_articles) >= 10:
                        return news_articles
    except Exception as e:
        logger.error(f"News error: {e}")
    return news_articles

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_user(update.effective_user.id)
    news_links = get_news()
    response = "📰 Latest sports news:\n\n" + "\n".join(f"• {link}" for link in news_links) if news_links else "❌ Couldn't fetch news"
    await update.message.reply_text(response)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text.split('_', 1)
    if len(command) < 2:
        await update.message.reply_text("Usage: /price_bitcoin")
        return
    
    crypto = command[1].lower()
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
        data = requests.get(url).json()
        if crypto in data:
            await update.message.reply_text(f"💎 {crypto.capitalize()}: ${data[crypto]['usd']:,.2f}")
        else:
            await update.message.reply_text("❌ Crypto not found")
    except Exception as e:
        await update.message.reply_text("⚠️ API error")

async def random_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    users = load_users()
    if not users:
        return

    user_id = random.choice(list(users.keys()))
    messages = [
        "👋 Hello! Remember I can show crypto prices!",
        "💰 Check BTC price with /btc_price",
        "📰 Try /news for latest updates",
        "💡 Need help? Use /help",
        "سلام مشتی! اگه کمک نیاز داشتی درخدمتم",
        "😼 میو 😼"
    ]
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=random.choice(messages)
        )
    except Exception as e:
        remove_user(user_id)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    handlers = [
        CommandHandler("start", start),
        CommandHandler("help", help_command),
        CommandHandler("news", news),
        CommandHandler("btc_price", get_btc_price),
        CommandHandler("price_bitcoin", price_command),
        CommandHandler("price_ethereum", price_command),
        CommandHandler("price_solana", price_command),
        CommandHandler("price_cardano", price_command),
        CommandHandler("price_dogecoin", price_command),
        CommandHandler("optout", optout),
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    ]
    for handler in handlers:
        application.add_handler(handler)

    application.job_queue.run_repeating(random_message, interval=300, first=300)
    application.job_queue.run_repeating(send_channel_update, interval=30, first=10)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()