import asyncio
from datetime import datetime

import editdistance
import httpx
import pymongo
import yaml
from html2text import html2text

from database import Database
from logger_creator import get_logger

log = get_logger(logger_name="Monitoring", filename="monitoring.log")


class MonitoringConfig:
    cfg = yaml.load(open("config/monitoring.yaml", "r"), Loader=yaml.Loader)

    changed_sym_threshold = cfg["changed_sym_threshold"]
    sleep_time = cfg["sleep_time"]


async def add_to_monitor_list(*, id: str, url: str, content: str):
    timestamp = datetime.utcnow()
    log.info(f"Adding to monitor list: id={id}, url={url}")
    await Database.url_collection.update_one(
        {f"{id}.url": url},
        {"$set": {id: {"url": url, "content": content, "timestamp": timestamp}}},
        upsert=True,
    )


async def delete_from_monitor_list(*, id: str, url: str):
    log.info(f"Deleting from monitor list: id={id}, url={url}")
    await Database.url_collection.delete_many({f"{id}.url": url})


async def get_initial_content(*, id: str, url: str):
    initial_content = (
        Database.url_collection.find({f"{id}.url": url})
        .sort(f"{id}.timestamp", pymongo.DESCENDING)
        .limit(1)
    )
    item = (await initial_content.to_list(1))[0]
    return item[id]["content"]


async def monitor_changes():
    while True:
        async for row in Database.url_collection.find():
            for id, value in row.items():
                if id != "_id":
                    url = value["url"]
                    old_content = await get_initial_content(id=id, url=url)
                    log.info(f"Checking for {id} url {url}")
                    try:
                        content = html2text((await httpx.get(url)).text)
                        if (
                            editdistance.eval(old_content, content)
                            > MonitoringConfig.changed_sym_threshold
                        ):
                            log.info(f"Found changes for {id} at {url}")
                            yield id, url, content
                    except Exception:
                        log.exception(f"Failed to check for {id} url {url}")
        await asyncio.sleep(MonitoringConfig.sleep_time)


async def monitor_loop(bot):
    async for id, url, content in monitor_changes():
        await bot.send_message(int(id), f"Url {url} has changed!")
        await add_to_monitor_list(id=id, url=url, content=content)
