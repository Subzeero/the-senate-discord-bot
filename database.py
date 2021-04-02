# Wrapper for Replit's databases.

from replit import db

def validate_server(serverId: int):
	serverId = str(serverId)
	server_data = {
		"reaction_roles": [],
		"custom_roles": {}
	}

	if not serverId in db.keys():
		db[serverId] = server_data
	else:
		server_data = db[serverId]

	return server_data

def get_server(serverId: int):
	serverId = str(serverId)
	return db[serverId]

def set_server(serverId: int, newServerData: dict):
	serverId = str(serverId)
	db[serverId] = newServerData

def get(key):
	return db[key]

def set(key, value):
	db[key] = value

def get_keys():
	return db.keys()
	