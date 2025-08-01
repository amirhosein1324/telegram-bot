# Telegram News & Crypto Bot

A feature-rich Telegram bot built with Python that delivers sports news, cryptocurrency prices, and random helpful messages to your users. The bot scrapes the latest headlines from [Varzesh3](https://www.varzesh3.com/), fetches up-to-date crypto prices from CoinGecko, and provides various interactive commands.
if a news comes into varzesh3 website you will have it in your telegram channel too.
## Features

- **Sports News:** Get the latest headlines directly from Varzesh3.
- **Cryptocurrency Prices:** Retrieve Bitcoin and other crypto prices (via CoinGecko).
- **Random Reminders:** Sends occasional helpful or fun messages to users.
- **User Opt-in/Opt-out:** Users can control whether they receive random messages.
- **Channel Updates:** Automated channel update messages.
- **Persian (Farsi) and English Support:** Some messages include Persian support.

## Commands

| Command                 | Description                                     |
|-------------------------|-------------------------------------------------|
| `/start`                | Welcome message and bot intro                   |
| `/help`                 | List all available commands                     |
| `/btc_price`            | Show current Bitcoin price                      |
| `/news`                 | 10 Latest sports news (Varzesh3)                |
| `/price_<coin>`         | Price for any supported coin (e.g. bitcoin)     |
| `/price_bitcoin`        | Shortcut for Bitcoin price                      |
| `/price_ethereum`       | Shortcut for Ethereum price                     |
| `/optout`               | Stop receiving random messages                  |

## Getting Started

### Prerequisites

- Python 3.9+
- [Telegram Bot Token](https://core.telegram.org/bots#6-botfather)
- [A Telegram Channel](https://core.telegram.org/bots#botfather) (for channel posting, optional)

### Required Python Libraries

Install dependencies:
```bash
pip install python-telegram-bot beautifulsoup4 requests jdatetime
```

### Setup
1. **Configure the bot:**
   - Edit `Telegram_bot.py` and replace the following placeholders:
     - `BOT_TOKEN` — Paste your Telegram Bot API token.
     - `CHANNEL_ID` — Your channel’s username (e.g., `@yourchannel`).

2. **Run the bot:**
   ```bash
   python Telegram_bot.py
   ```

## File Structure

- `Telegram_bot.py` — Main bot source code
- `users.json` — Stores opted-in users (auto-created)
- `runtime.json` — Stores runtime data/state (auto-created)

## Notes

- The bot scrapes news from Varzesh3 and may be affected if their website structure changes.
- All user and runtime data is stored locally in JSON files.
---

Feel free to copy, modify, and use this README for your project. Let me know if you want to add badges, example screenshots, or further customization!
