import discord, os, time
from discord import app_commands
from discord.ext import commands
from database.db import Database as db
from utils import checks

class extensions(commands.Cog, name = "Extensions"):
	"""Manage the bot's extensions."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		self.ext_dirs = ["cogs", "bot/cogs"]
		self.loaded_cogs = []
		self.unloaded_cogs = []
		self.all_cogs = []

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	@app_commands.describe(cog="The cog to load.")
	async def load(self, interaction: discord.Integration, cog: str) -> None:
		"""Load a cog."""

		await self.bot.load_extension(f"cogs.{cog}")

		bot_data = db.find_one("bot")
		if not cog in bot_data["loaded_cogs"]:
			bot_data["loaded_cogs"].append(cog)
			db.replace_one("bot", data = bot_data)

		await interaction.response.send_message(embed=discord.Embed(description=f"✅ `{cog}` has been loaded.", colour=discord.Color.green()), ephemeral=True)

	@load.autocomplete("cog")
	async def load_autocomplete(self, interaction: discord.Interaction, current_cog: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=cog, value=cog) for cog in self.unloaded_cogs if current_cog in cog]

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	@app_commands.describe(cog="The cog to unload.")
	async def unload(self, interaction: discord.Integration, cog: str) -> None:
		"""Unload a cog."""

		await self.bot.unload_extension(f"cogs.{cog}")

		bot_data = db.find_one("bot")
		if cog in bot_data["loaded_cogs"]:
			bot_data["loaded_cogs"].remove(cog)
			db.replace_one("bot", data = bot_data)

		await interaction.response.send_message(embed=discord.Embed(description=f"✅ `{cog}` has been unloaded.", colour=discord.Color.green()), ephemeral=True)

	@unload.autocomplete("cog")
	async def unload_autocomplete(self, interaction: discord.Interaction, current_cog: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=cog, value=cog) for cog in self.loaded_cogs if current_cog in cog]

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	@app_commands.describe(cog="The cog to reload.")
	async def reload(self, interaction: discord.Integration, cog: str) -> None:
		"""Unload a cog."""

		await self.bot.unload_extension(f"cogs.{cog}")
		await self.bot.load_extension(f"cogs.{cog}")

		await interaction.response.send_message(embed=discord.Embed(description=f"✅ `{cog}` has been reloaded.", colour=discord.Color.green()), ephemeral=True)
	
	@reload.autocomplete("cog")
	async def reload_autocomplete(self, interaction: discord.Interaction, current_cog: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=cog, value=cog) for cog in self.loaded_cogs if current_cog in cog]

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	async def listcogs(self, interaction: discord.Interaction) -> None:
		"""List extension/cog information."""

		# await interaction.response.defer(thinking=True)
		
		self.loaded_cogs = []
		self.unloaded_cogs = []
		self.all_cogs = []

		for dir in self.ext_dirs:
			if os.path.exists(dir):
				ext_path = dir
				break
		else:
			await interaction.response.send_message(embed=discord.Embed(description="❌ A `cogs` folder could not be located.", colour=discord.Color.red()), ephemeral=True)
			return

		for cog in self.bot.cogs.values():
			self.loaded_cogs.append(cog.__class__.__name__)

		for file_name in os.listdir(ext_path):
			if file_name.endswith(".py"):
				file_name = file_name[:-3]
				if not file_name in self.loaded_cogs:
					self.unloaded_cogs.append(file_name)
		self.all_cogs = self.loaded_cogs.copy()
		self.all_cogs.extend(self.unloaded_cogs)
		self.all_cogs.sort()
		self.loaded_cogs.sort()
		self.unloaded_cogs.sort()

		embed = discord.Embed(
			title = 'Extension Information', 
			description = "The following cogs have been registered:", 
			colour = discord.Color.gold()
		)

		for cog in self.all_cogs:
			embed.add_field(
				name = cog, 
				value="✅ Loaded!" if cog in self.loaded_cogs else "⚠️ Not Loaded!",
				inline = True
			)
					
		# await interaction.followup.send(embed=embed)
		await interaction.response.send_message(embed=embed)

	@commands.command()
	@commands.is_owner()
	async def syncGuild(self, ctx: commands.Context) -> None:
		"""Sync all slash commands to this guild."""
		synced = await ctx.bot.tree.sync(guild = ctx.guild)
		await ctx.reply(embed=discord.Embed(description=f"✅ Successfully synced `{len(synced)}` commands to this guild.", colour=discord.Color.green()))

	@commands.command()
	@commands.is_owner()
	async def syncGlobal(self, ctx: commands.Context) -> None:
		"""Sync all slash commands to all guilds."""
		synced = await ctx.bot.tree.sync()
		await ctx.reply(embed=discord.Embed(description=f"✅ Successfully synced `{len(synced)}` commands globally.", colour=discord.Color.green()))

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(extensions(bot))
