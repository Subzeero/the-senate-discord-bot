import discord
from discord.ext import commands
from database.db import Database as db

activityReference = {
	"playing": discord.ActivityType.playing,
	"streaming": discord.ActivityType.streaming,
	"listening": discord.ActivityType.listening,
	"watching": discord.ActivityType.watching,
	"competing": discord.ActivityType.competing
}

statusReference = {
	"online": discord.Status.online,
	"idle": discord.Status.idle,
	"dnd": discord.Status.dnd,
	"invisible": discord.Status.invisible
}

def get_status():
	bot_data = db.find_one("bot", {})
	if bot_data["maintenance"]:
		return{
			"activity": discord.Activity(type = activityReference["playing"], name = "MAINTENANCE"),
			"status": statusReference["dnd"]
		}
	else:
		return{
				"activity": discord.Activity(type = activityReference[bot_data["activity"]], name = bot_data["message"]),
				"status": statusReference[bot_data["status"]]
			}

async def update_status(client):
	bot_data = db.find_one("bot", {})

	if bot_data["maintenance"]:
		await client.change_presence(
			activity = discord.Activity(type = activityReference["playing"], name = "MAINTENANCE"),
			status = statusReference["dnd"]
		)
	else:
		await client.change_presence(
				activity = discord.Activity(type = activityReference[bot_data["activity"]], name = bot_data["message"]),
				status = statusReference[bot_data["status"]]
			)

def get_reference_table(referenceType):
	if referenceType == "activity":
		return activityReference
	elif referenceType == "status":
		return statusReference
	else:
		return