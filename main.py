# Imports
import discord, os, math, json, time, replit

from discord.ext import commands
from replit import db
from stayin_alive import keep_alive

bot = commands.Bot(command_prefix=";")
modRoleId = 767956851772882944
suggestionsChannelId = 796553486677311510

JSON_DB = None
activeMutes = []

spamming = False

# Fetch bot authentication token
botToken = os.getenv("BOT_TOKEN")

# Bot Events
@bot.event # On initial startup
async def on_ready():
	print("Bot Running.")
	await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "over you :D"))

@bot.event # Report permission errors
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the necessary permissions to run this command.')


@bot.event # Add reactions to messages sent in #server-suggestions
async def on_message(message):
	if message.channel.id == suggestionsChannelId:
		await message.add_reaction("👍")
		await message.add_reaction("👎")
	await bot.process_commands(message)

# Bot Commands
@bot.command(name = "[WIP] restart")
@commands.has_role(modRoleId)
async def restart(ctx):
	'''
	Force the bot to restart.
	'''

	#Closes discord's connection and gets systemd to restart.
	bot.close()

@bot.command()
@commands.has_role(modRoleId)
async def react(ctx, messageId:int, emoji:str):
	'''
	Add a reaction to the specified message.
	'''

	await ctx.message.delete()

	message = await ctx.fetch_message(messageId)
	await message.add_reaction(emoji)

@bot.command()
async def ping(ctx):
	'''
	Check the ping time of the bot.
	'''

	#Get the latency and send it to the user
	latency = str(math.floor(bot.latency * 1000))
	await ctx.send("Pong! `(" + latency + " ms)`")


@bot.command()
@commands.has_role(modRoleId)
async def echo(ctx, *, content: str):
	'''
	Echo a message back from bot.
	'''

	# Delete the previous message and send one from the bot.
	await ctx.message.delete()

	await ctx.send(content)


@bot.command()
@commands.has_role(modRoleId)
async def spam(ctx, *, content: str):
	'''
	Start a spamming rampage.
	'''

	# Delete the command and begin the spam loop.
	await ctx.message.delete()

	global spamming
	spamming = True

	text = content or "Spam."

	while spamming:
		await ctx.send(text)
		time.sleep(1)


@bot.command()
async def endspam(ctx):
	'''
	End the spam rampage.
	'''

	# End the spam loop.
	global spamming
	spamming = False

	await ctx.message.delete()

keep_alive()
bot.run(botToken)
