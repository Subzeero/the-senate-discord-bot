class VERSION1(object):
	BASE_STRUCTURE = {
		"SERVER_ID": 0,
		"DATA_VERSION": 1,
		"custom_prefix": None,
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

	@staticmethod
	def upgrade(version0_data):
		print("CANNOT UPGRADE FROM BASE VERSION.")
		return version0_data

DATABASE_VERSIONS = {
	1:VERSION1
}
