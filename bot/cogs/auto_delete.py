import discord
from discord.ext import commands
from database.db import Database as db
from utils import checks

ruleTypes = ["startswith", "endswith", "contains", "matches", "command"]

class auto_delete(commands.Cog, name = "Auto Delete"):
	"""Internal testing."""

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

	@commands.command()
	@commands.guild_only()
	@checks.is_admin()
	async def listAutoDeleteChannels(self, ctx):
		"""List the channels managed with auto delete and their rules."""

		guild_data = db.get_guild(ctx.guild.id)

		if not guild_data["auto_delete"]:
			embed = discord.Embed(
				description = "None!",
				colour = discord.Colour.gold()
			)
			embed.set_author(
				name = "Channels with Auto Delete Rules",
				icon_url = ctx.guild.icon.url
			)
		else:
			embed = discord.Embed(
				colour = discord.Colour.gold()
			)
			embed.set_author(
				name = "Channels with Auto Delete Rules",
				icon_url = ctx.guild.icon.url
			)

			for channelId in guild_data["auto_delete"]:
				channelObject = ctx.guild
				embed.add_field(
					name = str(channelObject),
					value = ""
				)

	@commands.command()
	@commands.guild_only()
	@checks.is_admin()
	async def addAutoDeleteChannel(self, ctx, channel: discord.TextChannel):
		"""Enable auto delete on a given channel."""

		guild_data = db.get_guild(ctx.guild.id)
		guild_data["auto_delete"][str(channel.id)] = {
			"enabled": False,
			"rules": []
		}

	@commands.command()
	@commands.guild_only()
	@checks.is_admin()
	async def editAutoDeleteChannelRules(self, ctx, channel:discord.TextChannel, editOption:str = None, ruleType:str = None, ruleExpression:str = None):
		"""Edit the rules of a channel managed with auto delete."""

		guild_data = db.get_guild(ctx.guild.id)
		if not str(channel.id) in guild_data["auto_delete"]:
			return await ctx.send(f"❌ {channel.mention} has not been configured. Use `;addAutoDeleteChannel` to get it set up.")

		if editOption and editOption.lower() == "add" and ruleType and ruleType.lower() in ruleTypes and ruleExpression:
			pass

		elif editOption and editOption.lower() == "remove":
			pass

		else:
			if not guild_data["auto_delete"][str(channel.id)]["rules"]:
				embed = discord.Embed(
					description = "None!",
					colour = discord.Colour.gold()
				)
				embed.set_author(
					name = f"Auto Delete Rules for #{str(channel)}",
					icon_url = ctx.guild.icon.url
				)
				return await ctx.send(
					embed = embed
				)

			else:
				embed = discord.Embed(
					authorName = f"Auto Delete Rules for {str(channel)}",
					footer = "Call this command with the `add` or `remove` editOption to configure rules."
				)
				for rule in guild_data["auto_delete"][str(channel.id)]["rules"]:
					embed.add_field(
						name = rule["type"],
						value = rule["expression"],
						inline = True
					)

				await ctx.send(embed = embed)


	@commands.command()
	@commands.guild_only()
	@checks.is_admin()
	async def removeAutoDeleteChannel(self, ctx, channel: discord.TextChannel):
		"""Disable auto delete on a given channel."""

async def setup(client):
	await client.add_cog(auto_delete(client))
