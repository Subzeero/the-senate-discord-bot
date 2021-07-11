import discord, os
from discord.ext import commands
from database.db import Database as db

class Extensions(commands.Cog):
	"""Manages the bot's extensions."""

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.is_owner()
	async def load(self, ctx, extension):
		"""Load an extension."""

		await ctx.message.delete()

		self.client.load_extension(f"cogs.{extension}")

		bot_data = db.find_one("bot", {})
		if not extension in bot_data["loaded_cogs"]:
			bot_data["loaded_cogs"].append(extension)
			db.replace_one("bot", {}, bot_data)

		embed = discord.Embed(
			description = f"✅ `{extension}` has been loaded!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)
		
	@commands.command()
	@commands.is_owner()
	async def unload(self, ctx, extension):
		"""Unload an extension."""

		await ctx.message.delete()

		self.client.unload_extension(f"cogs.{extension}")

		bot_data = db.find_one("bot", {})
		if extension in bot_data["loaded_cogs"]:
			bot_data["loaded_cogs"].remove(extension)
			db.replace_one("bot", {}, bot_data)

		embed = discord.Embed(
			description = f"✅ `{extension}` has been unloaded!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def reload(self, ctx, extension):
		"""Reload an extension."""

		await ctx.message.delete()

		self.client.unload_extension(f"cogs.{extension}")
		self.client.load_extension(f"cogs.{extension}")

		embed = discord.Embed(
			description = f"✅ `{extension}` has been reloaded!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def listcogs(self, ctx):
		'''
		List cog information.
		'''

		cogDict = {}

		for fileName in os.listdir("./cogs"):
			if fileName.endswith(".py"):
				try:
					self.client.load_extension(f"cogs.{fileName[:-3]}")
				except commands.ExtensionAlreadyLoaded:
					cogDict[fileName[:-3]] = "✅ Loaded!"
				except commands.ExtensionNotFound:
					cogDict[fileName[:-3]] = "❌ Not Found!"
				else:
					cogDict[fileName[:-3]] = "❎ Not Loaded!"
					self.client.unload_extension(f"cogs.{fileName[:-3]}")

		print(cogDict)
		print(self.client.cogs)

		embed = discord.Embed(
			title = 'Extension Information', 
			description = "The following cogs have been registered:", 
			colour = discord.Color.gold())

		for cogName in cogDict:
			embed.add_field(
				name = cogName, 
				value = cogDict[cogName], 
				inline = True
			)
					
		await ctx.send(embed = embed)

def setup(client):
	client.add_cog(Extensions(client))
