from motor.motor_asyncio import AsyncIOMotorClient

from userbot.config import config

client = AsyncIOMotorClient(host=config.db.host,
                            port=config.db.port)

db = client[config.db.name]
users = db['users']
