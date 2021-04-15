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

async def update_status():
	status_data = db.get("bot_status")

	if status_data["maintenance"]:
		await discord.Client.change_presence(
			activity = discord.Activity(type = activityReference["playing"], name = "maintenance mode."),
			status = activityReference["dnd"]
		)
	else:
		await discord.Client.change_presence(
				activity = discord.Activity(type = activityReference[status_data["activity"]], name = status_data["message"]),
				status = activityReference[status_data["status"]]
			)
