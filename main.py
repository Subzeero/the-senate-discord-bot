# The Senate Discord Bot
# Subzeero
# Development code for The Senate Discord Bot


# Imports
import discord, os

from discord.ext import commands
from pretty_help import PrettyHelp

from replit import db
from stayin_alive import keep_alive

client = commands.Bot(command_prefix=";", help_command = PrettyHelp(color = discord.Color.gold()))

modRoleId = 767956851772882944
hackerRoleId = 745863515998519360
suggestionsChannelId = 796553486677311510

activeMutes = []
spamming = False
suggestionReactionsEnabled = True

#Startup web server to prevent sleep
keep_alive()

# Load cogs
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