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
import jdatetime
import re

BOT_TOKEN = "PASTE YOURE TELEGRAM BOT TOKEN HERE"
USER_FILE = 'users.json'
RUNTIME_FILE = 'runtime.json'
CHANNEL_ID = "@YOURE TELEGRAM CHANNEL ID"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}

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

def save_runtime(start_time=None, last_success_time=None):
    data = {}
    if os.path.exists(RUNTIME_FILE):
        with open(RUNTIME_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass

    if start_time:
        data["start_time"] = start_time.isoformat()
    if last_success_time:
        data["last_success_time"] = last_success_time.isoformat()

    with open(RUNTIME_FILE, 'w') as f:
        json.dump(data, f)

def load_runtime():
    if os.path.exists(RUNTIME_FILE):
        with open(RUNTIME_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def get_latest_news_id_from_site():
    try:
        response = requests.get("https://www.varzesh3.com/", headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all("div", {"class": "news-main-list"})

        max_id = 0
        for div in divs:
            for a_tag in div.find_all("a", href=True):
                match = re.search(r"/news/(\d+)", a_tag["href"])
                if match:
                    news_id = int(match.group(1))
                    if news_id > max_id:
                        max_id = news_id
        return max_id
    except Exception as e:
        logger.error(f"Failed to fetch latest news ID: {e}")
        return 0

async def check_and_send_new_news(context: ContextTypes.DEFAULT_TYPE):
    runtime = load_runtime()
    last_news_id = int(runtime.get("last_news_id", 0))

    try:
        response = requests.get("https://www.varzesh3.com/", headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all("div", {"class": "news-main-list"})
        sent_count = 0
        max_news_id = last_news_id

        for div in divs:
            for a_tag in div.find_all("a", href=True):
                title = a_tag.get("title") or a_tag.get_text(strip=True)
                href = a_tag["href"]
                full_url = f"https://www.varzesh3.com{href}" if href.startswith("/") else href

                match = re.search(r"/news/(\d+)", href)
                if not match:
                    continue
                news_id = int(match.group(1))

                if news_id <= last_news_id:
                    continue

                title = title.strip()
                if not title:
                    continue
                await context.bot.send_message(chat_id=CHANNEL_ID, text=f"\U0001F195 {title}\n{full_url}")
                sent_count += 1

                if news_id > max_news_id:
                    max_news_id = news_id

        if sent_count > 0:
            save_runtime(last_success_time=datetime.now())
            with open(RUNTIME_FILE, 'r') as f:
                data = json.load(f)
            data['last_news_id'] = max_news_id
            with open(RUNTIME_FILE, 'w') as f:
                json.dump(data, f)

            logger.info(f"✅ Sent {sent_count} new news item(s).")
        else:
            logger.info("ℹ️ No new news found.")

    except Exception as e:
        logger.error(f"❌ Failed to fetch/send news: {e}")

async def send_channel_update(context: ContextTypes.DEFAULT_TYPE):
    try:
        now = datetime.now()
        message = (
            f"\U0001F504 Channel Update\n\n"
            f"📅 Date: {now.strftime('%Y-%m-%d')}\n"
            f"⏰ Time: {now.strftime('%H:%M:%S')}\n"
            "✅ Updated"
        )
        await context.bot.send_message(chat_id=CHANNEL_ID, text=message)
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
        "- you can check any crypto price with:(/price cryptoname)\n"
        "- help command (/help)\n\n"
        "You'll occasionally receive random messages from me. "
        "Use /optout if you don't want these."
    )
    await update.message.reply_text(welcome_msg, parse_mode='HTML', reply_markup=ForceReply(selective=True))

async def optout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    remove_user(user_id)
    await update.message.reply_text("You've been removed from messaging list. Use /start to re-enable.")

async def get_btc_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_user(update.effective_user.id)
    try:
        response = requests.get("https://blockchain.info/ticker").json()
        await update.message.reply_text(f"💰 BTC price now: {response['USD']['buy']}$")
    except Exception:
        await update.message.reply_text("⚠️ Couldn't fetch BTC price")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📋 Available commands:\n\n"
        "/start - Welcome message\n"
        "/help - This message\n"
        "/btc_price - Bitcoin price\n"
        "/news - Latest sports news\n"
        "/price_<coin> - Crypto price (e.g. /price_bitcoin)\n"
        "/optout - Stop random messages"
    )
    await update.message.reply_text(help_text)

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_user(update.effective_user.id)
    try:
        response = requests.get("https://www.varzesh3.com/", headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all("div", {"class": "news-main-list"})

        news_list = []
        for div in divs:
            for a_tag in div.find_all("a", href=True):
                title = a_tag.get("title") or a_tag.get_text(strip=True)
                href = a_tag["href"]
                full_url = f"https://www.varzesh3.com{href}" if href.startswith("/") else href

                if not title.strip():
                    continue
                if re.search(r"/news/\d+", href):
                    news_list.append(f"{len(news_list)+1}. {title.strip()}\n{full_url}")
                    if len(news_list) >= 5:  
                        break
            if len(news_list) >= 10:
                break

        if news_list:
            message = "\n\n".join(news_list)
            await update.message.reply_text(f"🗞️ Latest News:\n\n{message}")
        else:
            await update.message.reply_text("❌ No news items found.")
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to fetch news.")
        logger.error(f"Error in /news command: {e}")


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
    except Exception:
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
    ]
    try:
        await context.bot.send_message(chat_id=user_id, text=random.choice(messages))
    except Exception:
        remove_user(user_id)

def main() -> None:
    save_runtime(start_time=datetime.now())

    initial_news_id = get_latest_news_id_from_site()
    runtime_data = load_runtime()
    runtime_data["last_news_id"] = initial_news_id
    with open(RUNTIME_FILE, 'w') as f:
        json.dump(runtime_data, f)

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
        MessageHandler(filters.TEXT & ~filters.COMMAND, help_command)
    ]
    for handler in handlers:
        application.add_handler(handler)

    application.job_queue.run_repeating(random_message, interval = 800, first = 800)
    application.job_queue.run_repeating(send_channel_update, interval = 300, first = 30)
    application.job_queue.run_repeating(check_and_send_new_news, interval = 60, first = 0)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
