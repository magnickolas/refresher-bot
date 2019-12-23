import asyncio

from bot_initialize import start_bot
from logger_creator import get_logger
from monitoring import monitor_loop

log = get_logger(logger_name="Main", filename="main.log")


if __name__ == "__main__":
    bot = start_bot()
    log.info("Bot started!")

    asyncio.run_coroutine_threadsafe(monitor_loop(bot), asyncio.get_event_loop())

    bot.run_until_disconnected()
