import discord, os
from discord.ext import commands
from replit import db

class Extensions(commands.Cog):
	"""Manages the bot's extensions."""

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.is_owner()
	async def load(self, ctx, extension):
		"""Load an extension."""

		self.client.load_extension(f"cogs.{extension}")

		if "loadedCogs" in db.keys():
			loadedCogs = db["loadedCogs"]
			loadedCogs.append(extension)
			db["loadedCogs"] = loadedCogs
		else:
			db["loadedCogs"] = [extension]

		await ctx.send(f"✅ `{extension}` has been loaded!")

	@commands.command()
	@commands.is_owner()
	async def unload(self, ctx, extension):
		"""Unload an extension."""

		self.client.unload_extension(f"cogs.{extension}")

		if "loadedCogs" in db.keys():
			loadedCogs = db["loadedCogs"]
			if extension in loadedCogs:
				loadedCogs.remove(extension)
				db["loadedCogs"] = loadedCogs	
		else:
			db["loadedCogs"] = []

		await ctx.send(f"✅ `{extension}` has been unloaded!")

	@commands.command()
	@commands.is_owner()
	async def reload(self, ctx, extension):
		"""Reload an extension."""

		self.client.unload_extension(f"cogs.{extension}")
		self.client.load_extension(f"cogs.{extension}")

		await ctx.send(f"✅ `{extension}` has been reloaded!")

	@commands.command()
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

		embed = discord.Embed(
			title = 'Extension Information:', 
			description = "The following cogs have been registered:", 
			colour = discord.Color.gold())

		for cogName in cogDict:
			embed.add_field(
				name = cogName, 
				value = cogDict[cogName], 
				inline = True)
					
		await ctx.send(embed = embed)

def setup(client):
	client.add_cog(Extensions(client))