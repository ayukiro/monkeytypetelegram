import sqlite3
import aiohttp
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandStart
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            api_key TEXT NOT NULL
        )
        ''')
        conn.commit()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    start_text = (
        "I can search for user's statistics from monkeytype.com\n"
        "First of all, create and activate your API key [here](https://monkeytype.com/account-settings)\n"
        "Then insert it with /setapi"
    )
    await message.reply(start_text, parse_mode="Markdown", disable_web_page_preview=True)

@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    info_text = (
        "https://api.monkeytype.com/docs"
    )
    await message.reply(info_text, disable_web_page_preview=True)


def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"

def get_best_result(tests: list, language: str = None) -> dict:
    if not tests:
        return None
    
    if language:
        filtered_tests = [test for test in tests if test.get('language') == language]
        return max(filtered_tests, key=lambda x: x.get('wpm', 0)) if filtered_tests else None
    
    return max(tests, key=lambda x: x.get('wpm', 0))

async def get_monkeytype_stats(api_key: str, username: str):
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"ApeKey {api_key}",
            "Content-Type": "application/json"
        }
        url = f"https://api.monkeytype.com/users/{username}/profile"
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 471:
                    return {"error": 471}
                elif response.status == 429:
                    return {"error": 429}
                elif response.status == 401:
                	return {"error": 401}
                elif response.status == 200:
                    data = await response.json()
                    return data.get('data')
                return None
        except Exception as e:
            logging.error(f"Error fetching Monkeytype stats: {e}")
            return None

@dp.message(Command("setapi"))
async def set_api_key(message: types.Message):
    try:
        api_key = message.text.split(maxsplit=1)[1]
        if not api_key:
            await message.reply("Please provide your Monkeytype API key: /setapi YOUR_API_KEY")
            return

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO users (user_id, api_key) VALUES (?, ?)",
                         (message.from_user.id, api_key))
            conn.commit()
        
        await message.reply("Your Monkeytype API key has been successfully saved!")
    except IndexError:
        await message.reply("Please provide your Monkeytype API key: /setapi YOUR_API_KEY")
    except Exception as e:
        await message.reply("Error saving API key. Please try again.")
        logging.error(f"Error saving API key: {e}")

@dp.inline_query()
async def inline_query(inline_query: InlineQuery):
    try:
        username = inline_query.query.strip()
        if not username:
            return

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT api_key FROM users WHERE user_id = ?", (inline_query.from_user.id,))
            result = cursor.fetchone()
            
        if not result:
            no_api_result = InlineQueryResultArticle(
                id="no_api",
                title="API Key Not Set",
                description="Use /setapi command to set your Monkeytype API key first",
                input_message_content=InputTextMessageContent(
                    message_text="Please set your Monkeytype API key using /setapi command"
                )
            )
            await inline_query.answer(results=[no_api_result], cache_time=5)
            return

        api_key = result[0]
        stats = await get_monkeytype_stats(api_key, username)

        if stats is None:
            not_found_result = InlineQueryResultArticle(
                id="not_found",
                title="User Not Found",
                description=f"Could not find user: {username}",
                input_message_content=InputTextMessageContent(
                    message_text=f"Could not find Monkeytype user: {username}"
                )
            )
            await inline_query.answer(results=[not_found_result], cache_time=5)
            return

        if isinstance(stats, dict) and "error" in stats:
            if stats["error"] == 471:
                error_message = "API key isn't activated! Activate it first"
            elif stats["error"] == 429:
                error_message = "Too many requests, try again later"
            elif stats["error"] == 401:
            	error_message == "Authorization error! Try changing the API key"
            else:
                error_message = "An unknown error occurred"

            error_result = InlineQueryResultArticle(
                id="error",
                title="Error",
                description=error_message,
                input_message_content=InputTextMessageContent(message_text=error_message)
            )
            await inline_query.answer(results=[error_result], cache_time=5)
            return


        typing_stats = stats.get('typingStats', {})
        personal_bests = stats.get('personalBests', {})
        details = stats.get('details', {})
        
        # Get best results for different categories
        time_tests = personal_bests.get('time', {})
        word_tests = personal_bests.get('words', {})
        keyboard_text = f"⌨️ Keyboard: {details.get('keyboard')}\n\n" if details.get('keyboard') else "\n"

        stats_text = (
            f"📊 Monkeytype Stats for [{username}](https://monkeytype.com/profile/{username})\n"
            f"{keyboard_text}"
            f"🎯 Tests completed: {typing_stats.get('completedTests', 0)}\n"
            f"🚀 Started tests: {typing_stats.get('startedTests', 0)}\n"
            f"⏳ Time typing: {format_time(typing_stats.get('timeTyping', 0))}\n"
            f"🔥 Streaks (current and max): {stats.get('streak', 0)} / {stats.get('maxStreak', 0)} days\n\n"
            f"🏆 Best results:\n"
        )

        # Time mode bests
        for time_mode in ['15', '30', '60']:
            if time_mode in time_tests:
                best = get_best_result(time_tests[time_mode])
                if best:
                    stats_text += (
                        f"• {time_mode}s: {best.get('wpm', 0)} WPM "
                        f"({best.get('acc', 0):.1f}% acc, {best.get('language', 'unknown')})\n"
                    )

        # Word mode bests
        for word_mode in ['10', '25', '50', '100']:
            if word_mode in word_tests:
                best = get_best_result(word_tests[word_mode])
                if best:
                    stats_text += (
                        f"• {word_mode} words: {best.get('wpm', 0)} WPM "
                        f"({best.get('acc', 0):.1f}% acc, {best.get('language', 'unknown')})\n"
                    )

        result = InlineQueryResultArticle(
            id="stats",
            title=f"Monkeytype Stats - {username}",
            description=f"Tests: {typing_stats.get('completedTests', 0)}",
            input_message_content=InputTextMessageContent(
                message_text=stats_text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        )

        await inline_query.answer(results=[result], cache_time=30)

    except Exception as e:
        logging.error(f"Error in inline query: {e}")
        error_result = InlineQueryResultArticle(
            id="error",
            title="Error",
            description="An error occurred while fetching stats",
            input_message_content=InputTextMessageContent(
                message_text="An error occurred while fetching Monkeytype stats"
            )
        )
        await inline_query.answer(results=[error_result], cache_time=5)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
