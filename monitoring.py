import asyncio
from datetime import datetime

import httpx
import pymongo
import yaml
from html2text import html2text

import levenshtein_distance
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
    result = await Database.url_collection.delete_many({f"{id}.url": url})
    return result.deleted_count >= 1


async def get_initial_content(*, id: str, url: str):
    initial_content = (
        Database.url_collection.find({f"{id}.url": url})
        .sort(f"{id}.timestamp", pymongo.DESCENDING)
        .limit(1)
    )
    item = (await initial_content.to_list(1))[0]
    return item[id]["content"]


async def process(*, id, url):
    old_content = await get_initial_content(id=id, url=url)
    log.info(f"Checking for {id} url {url}")
    try:
        async with httpx.AsyncClient() as client:
            content = html2text((await client.get(url)).text)
            if (
                await levenshtein_distance.calculate(old_content, content)
            ) > MonitoringConfig.changed_sym_threshold:
                log.info(f"Found changes for {id} at {url}")
                return id, url, content
    except Exception:
        log.exception(f"Failed to check for {id} url {url}")


async def monitor_changes():
    while True:
        tasks = [
            process(id=id, url=value["url"])
            async for row in Database.url_collection.find()
            for id, value in row.items()
            if id != "_id"
        ]

        for completed_task in asyncio.as_completed(tasks):
            res = await completed_task
            if res is not None:
                id, url, content = res
                yield id, url, content

        await asyncio.sleep(MonitoringConfig.sleep_time)


async def monitor_loop(bot):
    async for id, url, content in monitor_changes():
        await bot.send_message(int(id), f"Url {url} has changed!")
        await add_to_monitor_list(id=id, url=url, content=content)
