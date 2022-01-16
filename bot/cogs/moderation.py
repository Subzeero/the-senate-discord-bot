import discord
from discord.ext import commands
from utils import checks, converters

class moderation(commands.Cog, name = "Moderation"):
	"""Moderation commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["delete"])
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.guild_only()
	@commands.check_any(checks.is_admin(), checks.is_mod())
	async def purge(self, ctx, numOfMessages: int, user: discord.User = None):
		"""Purge a number of messages."""

		numPurged = 0
		def purgeCheck(message):
			nonlocal numPurged
			if message.id == ctx.message.id:
				return True

			if message == response:
				return False

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

		response = await ctx.send("Working...")

		while True:
			if numPurged < numOfMessages:
				await ctx.channel.purge(limit = 15, check = purgeCheck)
			else:
				break

		embed = discord.Embed(
			description = f"✅ Successfully deleted {numOfMessages} messages.",
			colour = discord.Colour.gold()
		)

		embed.set_author(
			name = f"{ctx.author.name}#{ctx.author.discriminator}",
			icon_url = ctx.author.avatar_url
		)

		embed.set_footer(text = "This message will self-destruct in 10 seconds.")
		
		await response.edit(content = None, embed = embed, delete_after = 10)

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.guild_only()
	@commands.check_any(checks.is_admin(), checks.is_mod())
	async def react(self, ctx, messageId:int, *reactions:str):
		"""Add reactions to the specified message."""

		await ctx.message.delete()
		message = await ctx.fetch_message(messageId)
		reactionsStr = " ".join(reactions)

		for reaction in reactions:
			await message.add_reaction(reaction)

		embed = discord.Embed(
			description = f"✅ Successfully added {reactionsStr} to message #{messageId}.",
			colour = discord.Colour.gold()
		)

		embed.set_author(
			name = f"{ctx.author.name}#{ctx.author.discriminator}",
			icon_url = ctx.author.avatar_url
		)

		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

def setup(client):
	client.add_cog(moderation(client))
