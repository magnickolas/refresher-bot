from telethon import TelegramClient

from logger_creator import get_logger

log = get_logger(logger_name="Bot", filename="bot.log")


class BotRestricted(TelegramClient):
    def __init__(self, name, api_id, api_hash, *, proxy, white_list=None, **kwargs):
        super(BotRestricted, self).__init__(
            name, api_id, api_hash, proxy=proxy, **kwargs
        )
        self.white_list = white_list

    def check_white_list(self, id: int):
        log.info(f"Checking id {id}")
        if self.white_list is not None and id not in self.white_list:
            msg = f"BAD ID {id}"
            log.error(msg)
            raise Exception(msg)

    def on(self, event_pattern):
        def on_decorator(f):
            def wrapper(event):
                self.check_white_list(event.chat_id)
                return f(event)

            self.add_event_handler(wrapper, event_pattern)
            return wrapper

        return on_decorator
