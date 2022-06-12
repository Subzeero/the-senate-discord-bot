import discord, os
from discord.ext import commands
from database.db import Database as db

class extensions(commands.Cog, name = "Extensions"):
	"""Manage the bot's extensions."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["lo"])
	@commands.is_owner()
	async def load(self, ctx, extension):
		"""Load an extension."""

		await self.client.load_extension(f"cogs.{extension}")

		bot_data = db.find_one("bot")
		if not extension in bot_data["loaded_cogs"] and extension != "blank_custom":
			bot_data["loaded_cogs"].append(extension)
			db.replace_one("bot", data = bot_data)

		await ctx.message.add_reaction("✅")
		
	@commands.command(aliases = ["un"])
	@commands.is_owner()
	async def unload(self, ctx, extension):
		"""Unload an extension."""

		await self.client.unload_extension(f"cogs.{extension}")

		bot_data = db.find_one("bot")
		if extension in bot_data["loaded_cogs"]:
			bot_data["loaded_cogs"].remove(extension)
			db.replace_one("bot", data = bot_data)

		await ctx.message.add_reaction("✅")

	@commands.command(aliases = ["re"])
	@commands.is_owner()
	async def reload(self, ctx, extension):
		"""Reload an extension."""

		await self.client.unload_extension(f"cogs.{extension}")
		await self.client.load_extension(f"cogs.{extension}")

		await ctx.message.add_reaction("✅")

	@commands.command()
	@commands.is_owner()
	async def listcogs(self, ctx):
		"""List cog information."""

		loaded_cogs = []
		cogs = {}
		cogs_dirs = ["cogs", "bot/cogs"]
		cogs_path = ""

		for dir in cogs_dirs:
			if os.path.exists(dir):
				cogs_path = dir
				break
		else:
			await ctx.send("❌ No `cogs` folder could be located!")
			return

		for cog in self.client.cogs.values():
			loaded_cogs.append(cog.__class__.__name__)

		for fileName in os.listdir(cogs_path):
			if fileName.endswith(".py") and fileName != "blank_custom.py":
				if fileName[:-3] in loaded_cogs:
					cogs[fileName[:-3]] = "✅ Loaded!"
				else:
					cogs[fileName[:-3]] = "❎ Not Loaded!"

		embed = discord.Embed(
			title = 'Extension Information', 
			description = "The following cogs have been registered:", 
			colour = discord.Color.gold())

		for cog_name, cog_info in cogs.items():
			embed.add_field(
				name = cog_name, 
				value = cog_info, 
				inline = True
			)
					
		await ctx.send(embed = embed)

async def setup(client):
	await client.add_cog(extensions(client))
