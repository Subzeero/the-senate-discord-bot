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
	def insert(collection:str, data:dict):
		return Database.DB[collection].insert(data)

	@staticmethod
	def find(collection:str, query:dict):
		return Database.DB[collection].find(query)

	@staticmethod
	def find_one(collection:str, query:dict):
		return Database.DB[collection].find_one(query)

	@staticmethod
	def replace_one(collection:str, query:dict, data:dict, _upsert:bool = False):
		return Database.DB[collection].replace_one(query, data, upsert=_upsert)

	@staticmethod
	def delete(collection:str, query:dict):
		return Database.DB[collection].delete(query)

	@staticmethod
	def delete_one(collection:str, query:dict):
		return Database.DB[collection].delete_one(query)

	@staticmethod
	def get_server(serverId: int):
		server_data = Database.find_one(Database.SERVERS_COLLECTION, {"SERVER_ID":serverId})
		
		if server_data is None:
			server_data = DATABASE_VERSIONS[Database.LATEST_DATA_VERSION].BASE_STRUCTURE
		else:
			server_data_version = server_data["DATA_VERSION"]

			while server_data_version < Database.LATEST_DATA_VERSION:
				server_data = DATABASE_VERSIONS[server_data_version + 1].upgrade(server_data)
				server_data_version = server_data["DATA_VERSION"]

		return server_data

	@staticmethod
	def set_server(serverId: int, new_server_data: dict):
		return Database.replace_one(Database.SERVERS_COLLECTION, {"SERVER_ID":serverId}, new_server_data, True)
