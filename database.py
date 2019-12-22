import yaml
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCollection


class DatabaseConfig:
    cfg = yaml.load(open("config/mongodb.yaml", "r"), Loader=yaml.Loader)

    host = cfg["host"]
    port = cfg["port"]
    db_name = cfg["db_name"]


class Database:
    _client = AsyncIOMotorClient(DatabaseConfig.host, DatabaseConfig.port)
    _db = _client.get_database(DatabaseConfig.db_name)

    url_collection: AsyncIOMotorCollection = _db.get_collection("user_url")
