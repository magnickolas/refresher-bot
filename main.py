import asyncio

from bot_initialize import start_bot
from logger_creator import get_logger
from monitoring import monitor_loop

log = get_logger(logger_name="Main", filename="main.log")


if __name__ == "__main__":
    bot = start_bot()
    log.info("Bot started!")

    loop = asyncio.get_event_loop()
    loop.create_task(monitor_loop(bot))
    loop.run_forever()

    bot.run_until_disconnected()
