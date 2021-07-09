BASE_STRUCTURE = {
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

def UPGRADE(version0_data):
	print("CANNOT UPGRADE FROM BASE VERSION!")
