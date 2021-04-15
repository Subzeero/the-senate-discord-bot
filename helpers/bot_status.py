import discord
from discord.ext import commands
from database import db

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
