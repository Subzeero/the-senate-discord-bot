import os, pymongo
from database.data_versions import DATABASE_VERSIONS

class Database(object):
	if os.environ["DISCORD_BOT_ENV"] == "PROD":
		URI = os.environ["MONGODB_URI_PROD"]
		DB_NAME = os.environ["MONGODB_DB_PROD"]
	elif os.environ["DISCORD_BOT_ENV"] == "DEV":
		URI = os.environ["MONGODB_URI_DEV"]
		DB_NAME = os.environ["MONGODB_DB_DEV"]

	DB = None
	SERVERS_COLLECTION = "servers"
	LATEST_DATA_VERSION = 1

	@staticmethod
	def init():
		client = pymongo.MongoClient(Database.URI)
		Database.DB = client[Database.DB_NAME]

	@staticmethod
	def get_collections():
		return Database.DB.list_collection_names()

	@staticmethod
	def insert(collection:str, data:dict = {}):
		return Database.DB[collection].insert(data)

	@staticmethod
	def find(collection:str, query:dict = {}):
		return Database.DB[collection].find(query)

	@staticmethod
	def find_one(collection:str, query:dict = {}):
		return Database.DB[collection].find_one(query)

	@staticmethod
	def replace_one(collection:str, query:dict = {}, data:dict = {}, upsert:bool = False):
		return Database.DB[collection].replace_one(query, data, upsert=upsert)

	@staticmethod
	def delete(collection:str, query:dict = {}):
		return Database.DB[collection].delete(query)

	@staticmethod
	def delete_one(collection:str, query:dict = {}):
		return Database.DB[collection].delete_one(query)

	@staticmethod
	def get_guild(guild_id: int):
		guild_data = Database.find_one(Database.SERVERS_COLLECTION, {"SERVER_ID":guild_id})

		if guild_data is None:
			guild_data = DATABASE_VERSIONS[Database.LATEST_DATA_VERSION].BASE_STRUCTURE
			guild_data["SERVER_ID"] = guild_id
		else:
			guild_data_version = guild_data["DATA_VERSION"]

			while guild_data_version < Database.LATEST_DATA_VERSION:
				guild_data = DATABASE_VERSIONS[guild_data_version + 1].upgrade(guild_data)
				guild_data_version = guild_data["DATA_VERSION"]

		return guild_data

	@staticmethod
	def set_guild(guild_id: int, new_guild_data: dict):
		return Database.replace_one(Database.SERVERS_COLLECTION, {"SERVER_ID":guild_id}, new_guild_data, True)
