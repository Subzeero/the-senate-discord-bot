from database.db import Database as db

def get_debug_data():
	return db.find_one("debug", {})
