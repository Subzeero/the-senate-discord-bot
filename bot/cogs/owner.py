import discord
from discord.ext import commands
from database.db import Database as db
from helpers import bot_status

class Owner(commands.Cog):
	"""Owner commands."""

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.is_owner()
	async def changeStatusType(self, ctx, newStatusStr:str):
		"""Change the bot's status type.
		Valid status types: `online`, `idle`, `dnd`, `invisible`."""
		
		await ctx.message.delete()

		statusReference = bot_status.get_reference_table("status")
		newStatusStr = newStatusStr.lower()

		if not newStatusStr in statusReference:
			await ctx.send("❌ That is not a valid status type!")
			return

		bot_data = db.find_one("bot", {})
		bot_data["status"] = newStatusStr
		db.replace_one("bot", {}, bot_data)

		await bot_status.update_status(self.client)

		embed = discord.Embed(
			description = "✅ Successfully changed the bot's status!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def changeStatusMessage(self, ctx, *, newStatusMessage: str):
		"""Change the bot's status.
		Any text is valid."""

		await ctx.message.delete()

		bot_data = db.find_one("bot", {})
		bot_data["message"] = newStatusMessage
		db.replace_one("bot", {}, bot_data)

		await bot_status.update_status(self.client)

		embed = discord.Embed(
			description = "✅ Successfully changed the bot's status message!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def changeStatusActivity(self, ctx, newActivityStr: str):
		"""Change the bot's activity.
		Valid activity types: `playing`, `streaming`, `listening`, `watching`, `competing`."""

		await ctx.message.delete()

		activityReference = bot_status.get_reference_table("activity")
		newActivityStr = newActivityStr.lower()
		
		if not newActivityStr in activityReference:
			await ctx.send("❌ That is not a valid activity type!")
			return
		
		bot_data = db.find_one("bot", {})
		bot_data["activity"] = newActivityStr
		db.replace_one("bot", {}, bot_data)

		await bot_status.update_status(self.client)

		embed = discord.Embed(
			description = "✅ Successfully changed the bot's activity!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def startMaintenance(self, ctx):
		"""Enter maintenance mode."""
		
		await ctx.message.delete()

		bot_data = db.find_one("bot", {})
		bot_data["maintenance"] = True
		db.replace_one("bot", {}, bot_data)

		await bot_status.update_status(self.client)

		embed = discord.Embed(
			description = "✅ Successfully enabled maintenance mode!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def stopMaintenance(self, ctx):
		"""End maintenance mode."""
		
		await ctx.message.delete()

		bot_data = db.find_one("bot", {})
		bot_data["maintenance"] = False
		db.replace_one("bot", {}, bot_data)

		await bot_status.update_status(self.client)

		embed = discord.Embed(
			description = "✅ Successfully disabled maintenance mode!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command(aliases = ["close", "stop"])
	@commands.is_owner()
	async def shutdown(self, ctx):
		"""Shutdown the bot."""

		await ctx.message.delete()
		await self.client.change_presence(status = discord.Status.invisible)
		await self.client.close()


def setup(client):
	client.add_cog(Owner(client))
