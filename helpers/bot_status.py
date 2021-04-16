import discord
from discord.ext import commands
from database import db

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

async def update_status(client):
	status_data = db.get("bot_status")

	if status_data["maintenance"]:
		await client.change_presence(
			activity = discord.Activity(type = activityReference["playing"], name = "maintenance mode."),
			status = statusReference["dnd"]
		)
	else:
		await client.change_presence(
				activity = discord.Activity(type = activityReference[status_data["activity"]], name = status_data["message"]),
				status = statusReference[status_data["status"]]
			)

def get_reference(referenceType):
	if referenceType == "activity":
		return activityReference
	elif referenceType == "status":
		return statusReference
	else:
		return