import copy

class GUILD_VERSION3(object):
	BASE_STRUCTURE = {
		"GUILD_ID": 0,
		"DATA_VERSION": 3,
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
		"reaction_roles": []
	}

	@staticmethod
	def create(guild_id: int) -> dict:
		new_data = copy.deepcopy(GUILD_VERSION3.BASE_STRUCTURE)
		new_data["GUILD_ID"] = guild_id
		return new_data

	@staticmethod
	def upgrade(version2_data: dict) -> dict:
		version3_data = version2_data
		version3_data.pop("admin_roles")
		version3_data.pop("mod_roles")
		version3_data["DATA_VERSION"] = 3
		return version3_data


class GUILD_VERSION2(object):
	BASE_STRUCTURE = {
		"GUILD_ID": 0,
		"DATA_VERSION": 2,
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
	def create(guild_id: int) -> dict:
		new_data = copy.deepcopy(GUILD_VERSION2.BASE_STRUCTURE)
		new_data["GUILD_ID"] = guild_id
		return new_data

	@staticmethod
	def upgrade(version1_data: dict) -> dict:
		version2_data = version1_data
		version2_data["action_log"] = GUILD_VERSION2.BASE_STRUCTURE["action_log"]
		version2_data["DATA_VERSION"] = 2
		return version2_data


class GUILD_VERSION1(object):
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
	def create(guild_id: int) -> dict:
		new_data = copy.deepcopy(GUILD_VERSION1.BASE_STRUCTURE)
		new_data["GUILD_ID"] = guild_id
		return new_data

	@staticmethod
	def upgrade(version1_data: dict) -> dict:
		print("CANNOT UPGRADE FROM BASE VERSION.")
		return version1_data


class BOT_VERSION2(object):
	BASE_STRUCTURE = {
		"DATA_VERSION": 2,
		"activity": "watching",
		"status": "online",
		"message": "over you.",
		"maintenance": False,
		"loaded_cogs": [
			"owner",
			"error_handler"
		],
		"timers": []
	}

	@staticmethod
	def create() -> dict:
		return copy.deepcopy(BOT_VERSION2.BASE_STRUCTURE)

	@staticmethod
	def upgrade(version1_data: dict) -> dict:
		version2_data = version1_data
		version2_data["timers"] = BOT_VERSION2.BASE_STRUCTURE["timers"]
		version2_data["DATA_VERSION"] = 2
		return version2_data


class BOT_VERSION1(object):
	BASE_STRUCTURE = {
		"DATA_VERSION": 1,
		"activity": "watching",
		"status": "online",
		"message": "over you.",
		"maintenance": False,
		"loaded_cogs": [
			"owner",
			"error_handler"
		]
	}

	@staticmethod
	def create() -> dict:
		return copy.deepcopy(BOT_VERSION1.BASE_STRUCTURE)

	@staticmethod
	def upgrade(version1_data: dict) -> dict:
		print("CANNOT UPGRADE FROM BASE VERSION.")
		return version1_data

LATEST_DATA_VERSION = {
	"GUILD":2,
	"BOT": 1
}

DATABASE_VERSIONS = {
	"GUILD": {
		1:GUILD_VERSION1,
		2:GUILD_VERSION2,
		3:GUILD_VERSION3
	},
	"BOT": {
		1: BOT_VERSION1,
		2: BOT_VERSION2
	}
}
