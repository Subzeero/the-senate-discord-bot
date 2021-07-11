# The Senate Discord Bot
# Subzeero
# Development code for The Senate Discord Bot

# Imports
import discord, os
from database import db # Custom database wrapper

from discord.ext import commands
from pretty_help import PrettyHelp
from helpers import bot_status

# Declare Constants
BOT_ENV = os.environ["DISCORD_BOT_ENV"]
BOT_TOKEN = None
BOT_PREFIX = None

intents = discord.Intents.all() # All permissions/intents
status_data = bot_status.get_status()

db.init() # Initialize database

if BOT_ENV == "PROD":
	BOT_TOKEN = os.environ["DISCORD_TOKEN_PROD"]
	BOT_PREFIX = os.environ["DISCORD_BOT_PREFIX_PROD"]
elif BOT_ENV == "DEV":
	BOT_TOKEN = os.environ["DISCORD_TOKEN_DEV"]
	BOT_PREFIX = os.environ["DISCORD_BOT_PREFIX_DEV"]

def get_prefix(bot, message):
	custom_prefix = db.get_server(message.guild.id)["custom_prefix"]
	if custom_prefix is not None:
		return commands.when_mentioned_or(custom_prefix)(bot, message)
	else:
		return commands.when_mentioned_or(BOT_PREFIX)(bot, message)

client = commands.Bot( # Initialize bot settings
	command_prefix = get_prefix,
	intents = intents,
	case_insensitive = True,
	help_command = PrettyHelp(
		color = discord.Color.gold()
	),
	activity = status_data["activity"],
	status = status_data["status"]
)

# Load cogs on startup
for fileName in db.find_one("bot", {})["loaded_cogs"]:
	try:
		client.load_extension(f"cogs.{fileName}")
		print(f"Loaded {fileName}.")
	except:
		print(f"Failed to load {fileName}.")

client.run(BOT_TOKEN) # Run the bot
