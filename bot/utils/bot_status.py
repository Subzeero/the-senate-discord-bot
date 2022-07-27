import discord
from discord.ext import commands
from database.db import Database as db

activityReference = {
	"playing": discord.ActivityType.playing,
	"streaming": discord.ActivityType.streaming,
	"listening": discord.ActivityType.listening,
	"watching": discord.ActivityType.watching,
	"competing": discord.ActivityType.competing,
	"none": None
}

statusReference = {
	"online": discord.Status.online,
	"idle": discord.Status.idle,
	"dnd": discord.Status.dnd,
	"invisible": discord.Status.invisible
}

async def update_status(bot: commands.Bot) -> None:
	bot_data = await db.get_bot()

	if bot_data["maintenance"]:
		await bot.change_presence(
			activity = discord.Activity(type = activityReference["playing"], name = "MAINTENANCE"),
			status = statusReference["dnd"]
		)
	else:
		await bot.change_presence(
				activity = None if bot_data["activity"] is None else discord.Activity(type = activityReference[bot_data["activity"]], name = bot_data["message"]),
				status = statusReference[bot_data["status"]]
			)

def get_reference_table(referenceType):
	if referenceType == "activity":
		return activityReference
	elif referenceType == "status":
		return statusReference
	else:
		return