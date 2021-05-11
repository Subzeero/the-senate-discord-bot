# Wrapper for Replit's databases.

from replit import db

def validate_server(serverId: int):
	serverId = str(serverId)
	data_template = {
		"action_log": {
			"enabled": False
			"rules": [],
			"excluded_channels": []
		},
		"auto_delete": {},
		"auto_reactions": [],
		"custom_roles": {},
		"reaction_roles": [],
		"admin_roles": [],
		"mod_roles": [],
		"DATA_VERSION": 1
	}

	def recurseData(dataTemp, data): # VERIFY
		if isinstance(dataTemp, dict):
			for key, value in dataTemp.items():
				if not key in data:
					data[key] = value
					if isinstance(value, dict):
						return recurseData(dataTemp, data)

	if not serverId in db.keys():
		server_data = data_template
		db[serverId] = server_data

	else:
		server_data = db[serverId]
		for key, value in data_template.items():
			if not key in server_data:
				server_data[key] = value
		db[serverId] = server_data

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
