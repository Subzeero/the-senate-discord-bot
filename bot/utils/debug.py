from database.db import Database as db

async def get_debug_data():
	return await db.find_one("debug")
