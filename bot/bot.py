# The Senate Discord Bot
# Subzeero
# Main code file for The Senate Discord Bot

# Load Configuration
from utils import config

config.load_config()

# Imports
import asyncio, discord, os, traceback
from database.db import Database as db
from discord.ext import commands
from pretty_help import PrettyHelp
from utils import bot_status, checks, exceptions

# Declare Constants
BOT_ENV = os.environ["DISCORD_BOT_ENV"]
BOT_TOKEN = None
BOT_PREFIX = None

# Initialize database
db.init()

# Determine environment
if BOT_ENV == "PROD":
	BOT_TOKEN = os.environ["DISCORD_TOKEN_PROD"]
	BOT_PREFIX = os.environ["DISCORD_BOT_PREFIX_PROD"]
elif BOT_ENV == "DEV":
	BOT_TOKEN = os.environ["DISCORD_TOKEN_DEV"]
	BOT_PREFIX = os.environ["DISCORD_BOT_PREFIX_DEV"]

# Determine prefix
async def get_prefix(bot: commands.Bot, message: discord.Message):
	if message.guild == None:
		return commands.when_mentioned_or(BOT_PREFIX)(bot, message)

	custom_prefix = (await db.get_guild(message.guild.id))["custom_prefix"]
	if custom_prefix is not None:
		return commands.when_mentioned_or(custom_prefix)(bot, message)
	else:
		return commands.when_mentioned_or(BOT_PREFIX)(bot, message)

# Initialize bot
bot = commands.Bot(
	command_prefix = get_prefix,
	intents = discord.Intents.all(),
	case_insensitive = True,
	help_command = PrettyHelp(
		color = discord.Color.gold()
	)
)

# Global cooldown check
@bot.check
async def cooldown_check(ctx: commands.Context):
	on_cooldown, time = await checks.is_on_global_cooldown().predicate(ctx)
	if on_cooldown:
		raise exceptions.UserOnGlobalCooldown()
	else:
		return True

async def run_bot():
	async with bot:
		# Load previous cogs on startup
		print("Initializing The Senate Discord Bot...\n\nLoading Bot Extensions...")
		cog_data = (await db.get_bot())["loaded_cogs"]
		for fileName in cog_data:
			try:
				await bot.load_extension(f"cogs.{fileName}")
				print(f"Loaded {fileName}.")
			except Exception as error:
				print(f"Failed to load {fileName}")
				traceback.print_exception(type(error), error, error.__traceback__)
		
		# Start the bot
		print("\nComplete.\nStarting Bot...")
		await bot.start(BOT_TOKEN)

asyncio.run(run_bot())
