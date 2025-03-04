# Monkeytype Stats Bot

A Telegram bot that allows you to fetch and share Monkeytype user statistics using inline queries.

Created by Claude AI as experiment.

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

🎯 Tests completed: 692
🚀 Started tests: 7424
⌨️ Time typing: 9h 54m 54s

🏆 Best results:
• 15s: 133 WPM (95.5% acc, russian)
• 30s: 101 WPM (95.6% acc, russian)
• 60s: 95 WPM (94.8% acc, english)
• 100 words: 92 WPM (93.1% acc, russian)
```

## Other

More information about the API is available in the [official documentation](https://api.monkeytype.com/docs)

