# The Senate Discord Bot
# Subzeero
# Development code for The Senate Discord Bot

# Imports
import discord, os

from discord.ext import commands
from pretty_help import PrettyHelp

from replit import db
from stayin_alive import keep_alive

client = commands.Bot(
	command_prefix = ";",
	case_insensitive = True,
	help_command = PrettyHelp(
		color = discord.Color.gold()
	)
)

#Startup web server to prevent sleep
keep_alive()

# Load cogs on startup.
if "loadedCogs" in db.keys():
	for fileName in db["loadedCogs"]:
		try:
			client.load_extension(f"cogs.{fileName}")
			print(f"Loaded {fileName}.")
		except:
			print(f"Failed to load {fileName}.")
else:
	db["loadedCogs"] = []

client.run(os.getenv("DISCORD_TOKEN"))
