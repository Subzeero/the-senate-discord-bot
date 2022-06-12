import copy

class VERSION2(object):
	BASE_STRUCTURE = {
		"GUILD_ID": 0,
		"DATA_VERSION": 1,
		"custom_prefix": None,
		"action_log": {
			"enabled": False,
			"actions": {},
			"channel_id": 0
		},
		"auto_delete": {},
		"auto_reactions": [],
		"custom_roles": {
			"placement_role_id" : 0,
			"user_roles": {}
		},
		"reaction_roles": [],
		"admin_roles": [],
		"mod_roles": []
		}

	@staticmethod
	def create(guild_id):
		new_data = copy.deepcopy(VERSION2.BASE_STRUCTURE)
		new_data["GUILD_ID"] = guild_id
		return new_data

	@staticmethod
	def upgrade(database, version1_data):
		version2_data = version1_data
		version2_data["action_log"] = VERSION2.BASE_STRUCTURE["action_log"]
		version2_data["DATA_VERSION"] = 2
		database.set_guild(version2_data["GUILD_ID"], version2_data)
		return version2_data

class VERSION1(object):
	BASE_STRUCTURE = {
		"GUILD_ID": 0,
		"DATA_VERSION": 1,
		"custom_prefix": None,
		"action_log": {
			"enabled": False,
			"rules": [],
			"excluded_channels": []
		},
		"auto_delete": {},
		"auto_reactions": [],
		"custom_roles": {
			"placement_role_id" : 0,
			"user_roles": {}
		},
		"reaction_roles": [],
		"admin_roles": [],
		"mod_roles": []
		}

	@staticmethod
	def create(guild_id):
		new_data = copy.deepcopy(VERSION1.BASE_STRUCTURE)
		new_data["GUILD_ID"] = guild_id
		return new_data

	@staticmethod
	def upgrade(database, version1_data):
		print("CANNOT UPGRADE FROM BASE VERSION.")
		return version1_data

LATEST_DATA_VERSION = 2
DATABASE_VERSIONS = {
	1:VERSION1,
	2:VERSION2
}
