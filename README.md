# Monkeytype Stats Bot

A Telegram bot that allows you to fetch and share Monkeytype user statistics using inline queries.

**Created by Claude AI as experiment.**

## Setup

1. Install required packages:
```bash
pip install aiogram aiohttp
```

2. Create a new bot through [@BotFather](https://t.me/BotFather) and get the token

3. Replace `YOUR_BOT_TOKEN` in the code with your bot token

4. Run the bot:
```bash
python bot.py
```

## Usage

1. Start the bot and run `/start` to get initial instructions
2. Create and activate your Monkeytype API key at https://monkeytype.com/account-settings
3. Set your API key using the `/setapi YOUR_API_KEY` command
4. In any chat, type `@your_bot_username username` to fetch and share Monkeytype stats


## Example

```
📊 Monkeytype Stats for username
📈 Level 70 ▓▓▓▓░░░░░░ 
⌨️ Keyboard: aula f75, lubed

🎯 Tests completed: 695
🚀 Started tests: 7573
⏳ Time typing: 10h 1m 21s
🔥 Streaks (current and max): 2 / 28 days

🏆 Best results:
• 15s: 133.56 WPM (95.5% acc, russian)
• 30s: 101.2 WPM (95.6% acc, russian)
• 10 words: 142.63 WPM (100.0% acc, russian)
• 25 words: 127.29 WPM (98.0% acc, russian)
• 50 words: 100.06 WPM (96.9% acc, russian)
• 100 words: 92.7 WPM (93.1% acc, russian)5• 100 words: 92 WPM (93.1% acc, russian)
```

## Other

More information about the API is available in the [official documentation](https://api.monkeytype.com/docs)

