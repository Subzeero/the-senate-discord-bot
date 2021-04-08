# The Senate Discord Bot
# Subzeero
# Development code for The Senate Discord Bot

# Imports
import discord, os
import database as db # Custom database wrapper

from discord.ext import commands
from pretty_help import PrettyHelp

from stayin_alive import keep_alive # Webserver to keep the bot running

intents = discord.Intents.all() # All permissions

client = commands.Bot( # Initialize bot settings
	command_prefix = ";",
	intents = intents,
	case_insensitive = True,
	help_command = PrettyHelp(
		color = discord.Color.gold()
	)
)

#Startup web server to prevent sleep
keep_alive()

# Load cogs on startup
for fileName in db.get("loaded_cogs"):
	try:
		client.load_extension(f"cogs.{fileName}")
		print(f"Loaded {fileName}.")
	except:
		print(f"Failed to load {fileName}.")

client.run(os.getenv("DISCORD_TOKEN")) # Get bot token from secret ENV file and start running
