import yaml
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import ServerSelectionTimeoutError

from logger_creator import get_logger

log = get_logger(logger_name="Database", filename="database.log")


class DatabaseConfig:
    cfg = yaml.load(open("config/mongodb.yaml", "r"), Loader=yaml.Loader)

    host = cfg["host"]
    port = cfg["port"]
    db_name = cfg["db_name"]


class Database:
    _client = AsyncIOMotorClient(DatabaseConfig.host, DatabaseConfig.port)
    try:
        log.info("Connecting to database...")
        _client.is_mongos
    except ServerSelectionTimeoutError as ex:
        msg = "Failed to connect to database"
        log.exception(msg)
        raise ex
    else:
        log.info("Successfully connected to database")

    _db = _client.get_database(DatabaseConfig.db_name)

    url_collection: AsyncIOMotorCollection = _db.get_collection("user_url")
