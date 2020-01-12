import httpx
import socks
import yaml
from html2text import html2text
from telethon import events

from bot import BotRestricted
from logger_creator import get_logger
from monitoring import add_to_monitor_list
from monitoring import delete_from_monitor_list

log = get_logger(logger_name="BotInit", filename="bot_initialize.log")


def start_bot():
    bot_config = yaml.load(open("config/bot.yaml", "r"), Loader=yaml.Loader)

    name = bot_config["name"]
    api_id = bot_config["api_id"]
    api_hash = bot_config["api_hash"]
    bot_token = bot_config["bot_token"]
    proxy_config = bot_config["proxy"]
    proxy = None
    if proxy_config is not None:
        proxy_type = socks.PROXY_TYPES[proxy_config["type"]]
        proxy_host = proxy_config["host"]
        proxy_port = proxy_config["port"]
        proxy = (proxy_type, proxy_host, proxy_port)
    white_list = bot_config["white_list"]

    bot = BotRestricted(name, api_id, api_hash, proxy=proxy, white_list=white_list)
    init_handlers(bot)

    bot.start(bot_token=bot_token)
    return bot


def init_handlers(bot):
    @bot.on(events.NewMessage(pattern="/start"))
    async def start_handler(event):
        await event.respond(
            "Hey! You can send me url and I will check it for changes for you."
        )

    @bot.on(events.NewMessage(pattern="(?i)/m(onitor)? (.+)"))
    async def monitor_handler(event):
        id = str(event.chat_id)
        url = event.pattern_match.group(2)
        try:
            async with httpx.AsyncClient() as client:
                content = html2text((await client.get(url)).text)
        except Exception as ex:
            log.exception(ex)
            await event.respond(f'Incorrect url: "{url}"')
        await add_to_monitor_list(id=id, url=url, content=content)
        await event.respond(f"I will monitor {url} for you")

    @bot.on(events.NewMessage(pattern="(?i)/d(el|elete)? (.+)"))
    async def delete_handler(event):
        id = str(event.chat_id)
        url = event.pattern_match.group(2)
        if await delete_from_monitor_list(id=id, url=url):
            await event.respond(f"Stop monitoring {url}")
        else:
            await event.respond(f"Not found in monitor list {url}")

    return start_handler, monitor_handler, delete_handler
