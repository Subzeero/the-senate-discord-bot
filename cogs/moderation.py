import discord
from discord.ext import commands
from helpers import checks, embeds

class Moderation(commands.Cog):
	"""Moderation commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["delete"])
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.guild_only()
	@commands.check_any(checks.isAdmin(), checks.isMod())
	async def purge(self, ctx, numOfMessages: int, user: discord.User = None):
		"""Purge a number of messages."""

		numPurged = 0
		def purgeCheck(message):
			nonlocal numPurged
			if message.id == ctx.message.id:
				return True

			if numPurged >= numOfMessages:
				return False

			if user:
				if message.author.id == user.id:
					numPurged += 1
					return True
				else:
					return False
			else:
				numPurged += 1
				return True

		message = await ctx.send("Working...")

		while True:
			if numPurged < numOfMessages:
				await ctx.channel.purge(limit = 15, check = purgeCheck)
			else:
				break

		await message.edit(
			embed = embeds.tempEmbed(
				desc = f"✅ Successfully deleted {numOfMessages} messages.",
				author = ctx.author
			), 
			delete_after = 10
		)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.guild_only()
	@commands.check_any(checks.isAdmin(), checks.isMod())
	async def react(self, ctx, messageId:int, *reactions:str):
		"""Add reactions to the specified message."""

		await ctx.message.delete()
		message = await ctx.fetch_message(messageId)
		reactionsStr = " ".join(reactions)

		for reaction in reactions:
			await message.add_reaction(reaction)

		await ctx.send(
			embed = embeds.tempEmbed(
				desc = f"✅ Successfully added {reactionsStr} to message #{messageId}.",
				author = ctx.author
			),
			delete_after = 10
		)

def setup(client):
	client.add_cog(Moderation(client))
