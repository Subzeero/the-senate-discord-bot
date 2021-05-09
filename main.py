# The Senate Discord Bot
# Subzeero
# Development code for The Senate Discord Bot

# Imports
import discord, os
import database as db # Custom database wrapper

from discord.ext import commands
from pretty_help import PrettyHelp
from helpers import bot_status

# from helpers import stayin_alive # Webserver to keep the bot running; not required with Hacker plan

intents = discord.Intents.all() # All permissions
status_data = bot_status.get_status()

client = commands.Bot( # Initialize bot settings
	command_prefix = ";",
	intents = intents,
	case_insensitive = True,
	help_command = PrettyHelp(
		color = discord.Color.gold()
	),
	activity = status_data["activity"],
	status = status_data["status"]
)

#Startup web server to prevent sleep
# stayin_alive.keep_alive()

# Load cogs on startup
for fileName in db.get("loaded_cogs"):
	try:
		client.load_extension(f"cogs.{fileName}")
		print(f"Loaded {fileName}.")
	except:
		print(f"Failed to load {fileName}.")

client.run(os.environ['DISCORD_TOKEN']) # Get bot token from secret ENV file and start running
