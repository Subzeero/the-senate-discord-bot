import os
from pymongo import MongoClient

MONGO_USER = os.environ["MONGO_INITDB_ROOT_USERNAME"]
MONGO_PASS = os.environ["MONGO_INITDB_ROOT_PASSWORD"]

# MAKE THIS A CLASS
mongo_client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASS}@db:27017/")
db_object = mongo_client["the-senate-db"]

server_collection = db_object["servers"]

def validate_server(serverId: int):
	data_template = {
		"_id": 0,
		"custom_prefix": None,
		"DATA_VERSION": 1,
		"action_log": {
			"enabled": False,
			"rules": [],
			"excluded_channels": []
		},
		"auto_delete": {},
		"auto_reactions": [],
		"custom_roles": {},
		"reaction_roles": [],
		"admin_roles": [],
		"mod_roles": []
	}

	server_data = server_collection.find_one({"_id":serverId})

	if server_data is None:
		server_data = data_template
		server_data["_id"] = serverId
		server_collection.insert_one(server_data)
 
	return server_data

def get_server(serverId: int):
	server_data = server_collection.find_one({"_id":serverId})
	return server_data

def set_server(serverId: int, newServerData: dict):
	server_collection.replace_one({"_id":serverId}, newServerData, upsert=True)

def get_collection(collectionName):
	collection = db_object[collectionName]
	return collection.find_one()

def set_collection(collectionName, data: dict):
	collection = db_object[collectionName]
	collection.replace_one({})

def get_collections():
	return db_object.list_collection_names()
