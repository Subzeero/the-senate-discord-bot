# Imports
import discord, os, math, json, replit

from discord.ext import commands
from pretty_help import PrettyHelp
from asyncio import sleep
from replit import db
from stayin_alive import keep_alive

bot = commands.Bot(command_prefix=";", help_command = PrettyHelp(color = discord.Color.gold()))
modRoleId = 767956851772882944
hackerRoleId = 745863515998519360
suggestionsChannelId = 796553486677311510

JSON_DB = None
activeMutes = []

spamming = False
suggestionReactionsEnabled = True

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
        await ctx.send('You do not have the necessary permissions to run this command.', delete_after = 5)

@bot.event # Add reactions to messages sent in #server-suggestions
async def on_message(message):
	if message.channel.id == suggestionsChannelId and suggestionReactionsEnabled:
		await message.add_reaction("👍")
		await message.add_reaction("👎")
	await bot.process_commands(message)

# Bot Commands
@bot.command()
@commands.has_role(modRoleId)
async def restart(ctx):
	'''
	[WIP] Force the bot to restart.
	'''

	#Closes discord's connection and gets systemd to restart.
	bot.close()

@bot.command(name = 'perms', aliases = ['perms_for', 'permissions'])
@commands.guild_only()
async def check_permissions(ctx, *, member: discord.Member = None):
	'''
	Check the permissions of a user.
	'''

	if not member:
		member = ctx.author

	# Here we check if the value of each permission is True.
	perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

	# And to make it look nice, we wrap it in an Embed.
	embed = discord.Embed(title = 'Permissions for:', description = ctx.guild.name, colour = member.colour)
	embed.set_author(icon_url = member.avatar_url, name = str(member))

	# \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
	embed.add_field(name = '\uFEFF', value = perms)

	await ctx.send(content = None, embed = embed)

@bot.command(name = "ssreactions")
@commands.guild_only()
@commands.has_role(hackerRoleId)
async def suggestionReactions(ctx, toggle:bool):
	'''
	Toggle auto-reactions for #server-suggestions. 
	'''

	global suggestionReactionsEnabled
	suggestionReactionsEnabled = toggle

	await ctx.message.delete()
	start = "Enabled" if suggestionReactionsEnabled else "Disabled"
	await ctx.send("✅ " + start + " message reactions in #server-suggestions.", delete_after = 5)

@bot.command()
@commands.has_role(modRoleId)
async def react(ctx, messageId:int, *reactions:str):
	'''
	Adds reactions to the specified message.
	'''

	await ctx.message.delete()

	message = await ctx.fetch_message(messageId)

	for reaction in reactions:
		await message.add_reaction(reaction)

@bot.command()
async def ping(ctx):
	'''
	Check the ping time of the bot.
	'''

	#Get the latency and send it to the user
	latency = str(math.floor(bot.latency * 1000))
	await ctx.send("Pong! `(" + latency + " ms)`")

@bot.command()
async def senate(ctx):
	'''
	Declare supremacy.
	'''

	await ctx.message.delete()
	await ctx.send("https://tenor.com/view/star-wars-i-am-the-senate-gif-10270130")

@bot.command(aliases = ['e', 'say', 's'])
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
		await sleep(1)


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
