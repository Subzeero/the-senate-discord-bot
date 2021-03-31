# The Senate Discord Bot
# Subzeero
# Development code for The Senate Discord Bot

# Imports
import discord, os
import database as db # Custom database wrapper

from discord.ext import commands
from pretty_help import PrettyHelp

from stayin_alive import keep_alive

intents = discord.Intents.all()

client = commands.Bot(
	command_prefix = ";",
	intents = intents,
	case_insensitive = True,
	help_command = PrettyHelp(
		color = discord.Color.gold()
	)
)

#Startup web server to prevent sleep
keep_alive()

# Load cogs on startup.
if "loaded_cogs" in db.get_keys():
	for fileName in db.get("loaded_cogs"):
		try:
			client.load_extension(f"cogs.{fileName}")
			print(f"Loaded {fileName}.")
		except:
			print(f"Failed to load {fileName}.")
else:
	db.set("loaded_cogs", [])

client.run(os.getenv("DISCORD_TOKEN"))
