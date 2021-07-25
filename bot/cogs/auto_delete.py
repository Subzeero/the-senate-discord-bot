import discord
from discord.ext import commands
from database.db import Database as db
from helpers import checks

ruleTypes = ["startswith", "endswith", "contains", "matches", "command"]

class AutoDelete(commands.Cog):
	"""Internal testing."""

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

	@commands.command()
	@commands.guild_only()
	@checks.isAdmin()
	async def listAutoDeleteChannels(self, ctx):
		"""List the channels managed with auto delete and their rules."""

		server_data = db.get_server(ctx.guild.id)

		if not server_data["auto_delete"]:
			embed = discord.Embed(
				description = "None!",
				colour = discord.Colour.gold()
			)
			embed.set_author(
				name = "Channels with Auto Delete Rules",
				icon_url = ctx.guild.icon_url
			)
		else:
			embed = discord.Embed(
				colour = discord.Colour.gold()
			)
			embed.set_author(
				name = "Channels with Auto Delete Rules",
				icon_url = ctx.guild.icon_url
			)

			for channelId in server_data["auto_delete"]:
				channelObject = ctx.guild
				embed.add_field(
					name = str(channelObject),
					value = ""
				)

	@commands.command()
	@commands.guild_only()
	@checks.isAdmin()
	async def addAutoDeleteChannel(self, ctx, channel: discord.TextChannel):
		"""Enable auto delete on a given channel."""

		server_data = db.get_server(ctx.guild.id)
		server_data["auto_delete"][str(channel.id)] = {
			"enabled": False,
			"rules": []
		}

	@commands.command()
	@commands.guild_only()
	@checks.isAdmin()
	async def editAutoDeleteChannelRules(self, ctx, channel:discord.TextChannel, editOption:str = None, ruleType:str = None, ruleExpression:str = None):
		"""Edit the rules of a channel managed with auto delete."""

		server_data = db.get_server(ctx.guild.id)
		if not str(channel.id) in server_data["auto_delete"]:
			return await ctx.send(f"❌ {channel.mention} has not been configured. Use `;addAutoDeleteChannel` to get it set up.")

		if editOption and editOption.lower() == "add" and ruleType and ruleType.lower() in ruleTypes and ruleExpression:
			pass

		elif editOption and editOption.lower() == "remove":
			pass

		else:
			if not server_data["auto_delete"][str(channel.id)]["rules"]:
				embed = discord.Embed(
					description = "None!",
					colour = discord.Colour.gold()
				)
				embed.set_author(
					name = f"Auto Delete Rules for #{str(channel)}",
					icon_url = ctx.guild.icon_url
				)
				return await ctx.send(
					embed = embed
				)

			else:
				embed = discord.Embed(
					authorName = f"Auto Delete Rules for {str(channel)}",
					footer = "Call this command with the `add` or `remove` editOption to configure rules."
				)
				for rule in server_data["auto_delete"][str(channel.id)]["rules"]:
					embed.add_field(
						name = rule["type"],
						value = rule["expression"],
						inline = True
					)

				await ctx.send(embed = embed)


	@commands.command()
	@commands.guild_only()
	@checks.isAdmin()
	async def removeAutoDeleteChannel(self, ctx, channel: discord.TextChannel):
		"""Disable auto delete on a given channel."""

def setup(client):
	client.add_cog(AutoDelete(client))
