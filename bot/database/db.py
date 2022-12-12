import os, pymongo
import motor.motor_asyncio as motor
from database.data_versions import DATABASE_VERSIONS, LATEST_DATA_VERSION
from utils.exceptions import DatabaseInitializationError

class Database(object):
	if os.environ["DISCORD_BOT_ENV"] == "PROD":
		URI = os.environ["MONGODB_URI_PROD"]
		DB_NAME = os.environ["MONGODB_DB_PROD"]
	elif os.environ["DISCORD_BOT_ENV"] == "DEV":
		URI = os.environ["MONGODB_URI_DEV"]
		DB_NAME = os.environ["MONGODB_DB_DEV"]

	DB = None
	GUILDS_COL = None
	GUILDS_COL_STR = "guilds"
	BOT_COL = None
	BOT_COL_STR = "bot"

	@staticmethod
	def init() -> None:
		if Database.DB:
			raise DatabaseInitializationError("The database has already been initialized.")

		client = motor.AsyncIOMotorClient(Database.URI)
		Database.DB = client[Database.DB_NAME]
		Database.GUILDS_COL = Database.DB[Database.GUILDS_COL_STR]
		Database.BOT_COL = Database.DB[Database.BOT_COL_STR]

	@staticmethod
	async def get_collections() -> list[str]:
		return await Database.DB.list_collection_names()

	@staticmethod
	async def insert_one(collection:motor.AsyncIOMotorCollection | str, data:dict = {}) -> pymongo.results.InsertOneResult:
		if isinstance(collection, str):
			collection = Database.DB[collection]
		return await collection.insert_one(data)

	@staticmethod
	def find(collection:motor.AsyncIOMotorCollection | str, query:dict = {}) -> motor.AsyncIOMotorCursor:
		if isinstance(collection, str):
			collection = Database.DB[collection]
		return collection.find(query)

	@staticmethod
	async def find_one(collection:motor.AsyncIOMotorCollection | str, query:dict = {}) -> (dict | None):
		if isinstance(collection, str):
			collection = Database.DB[collection]
		return await collection.find_one(query)

	@staticmethod
	async def replace_one(collection:motor.AsyncIOMotorCollection | str, query:dict = {}, data:dict = {}, upsert:bool = False) -> pymongo.results.UpdateResult:
		if isinstance(collection, str):
			collection = Database.DB[collection]
		return await collection.replace_one(query, data, upsert=upsert)

	@staticmethod
	async def delete_one(collection:motor.AsyncIOMotorCollection | str, query:dict = {}) -> pymongo.results.DeleteResult:
		if isinstance(collection, str):
			collection = Database.DB[collection]
		return await collection.delete_one(query)

	@staticmethod
	async def get_bot() -> dict:
		bot_data = await Database.find_one(Database.BOT_COL)

		if bot_data is None:
			bot_data = DATABASE_VERSIONS["BOT"][LATEST_DATA_VERSION["BOT"]].create()
		else:
			bot_data_version = bot_data["DATA_VERSION"]

			while bot_data_version < LATEST_DATA_VERSION["BOT"]:
				bot_data = DATABASE_VERSIONS["BOT"][bot_data_version + 1].upgrade(bot_data)
				bot_data_version = bot_data["DATA_VERSION"]
			await Database.set_bot(bot_data)

		return bot_data

	@staticmethod
	async def set_bot(new_bot_data: dict) -> pymongo.results.UpdateResult:
		return await Database.replace_one(Database.BOT_COL, {}, new_bot_data, True)

	@staticmethod
	async def get_guild(guild_id: int) -> dict:
		guild_data = await Database.find_one(Database.GUILDS_COL, {"GUILD_ID":guild_id})

		if guild_data is None:
			guild_data = DATABASE_VERSIONS["GUILD"][LATEST_DATA_VERSION["GUILD"]].create(guild_id)
		else:
			guild_data_version = guild_data["DATA_VERSION"]

			while guild_data_version < LATEST_DATA_VERSION["GUILD"]:
				guild_data = DATABASE_VERSIONS["GUILD"][guild_data_version + 1].upgrade(guild_data)
				guild_data_version = guild_data["DATA_VERSION"]
			await Database.set_guild(guild_id, guild_data)

		return guild_data

	@staticmethod
	async def set_guild(guild_id: int, new_guild_data: dict) -> pymongo.results.UpdateResult:
		return await Database.replace_one(Database.GUILDS_COL, {"GUILD_ID":guild_id}, new_guild_data, True)
