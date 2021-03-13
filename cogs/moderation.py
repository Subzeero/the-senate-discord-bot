import discord
from discord.ext import commands
moderatorRole = 767956851772882944

class Moderation(commands.Cog):
	"""Moderation commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["delete"])
	@commands.has_role(moderatorRole)
	async def purge(self, ctx, numOfMessages: int, user = None):
		"""Purge a number of messages."""

		messagesToDelete = []

		async for message in ctx.channel.history(limit = numOfMessages + 1):
			messagesToDelete.append(message)

		await ctx.channel.delete_messages(messagesToDelete)

		embed = discord.Embed(
			#title = "Success",
			description = f"✅ Successfully deleted {numOfMessages} messages.",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command(aliases = ["r"])
	@commands.has_role(moderatorRole)
	async def react(self, ctx, messageId:int, *reactions:str):
		"""Add reactions to the specified message."""

		await ctx.message.delete()

		message = await ctx.fetch_message(messageId)
		
		for reaction in reactions:
			await message.add_reaction(reaction)

		embed = discord.Embed(
			#title = "Success!",
			description = f"✅ Successfully added {reactions} to message #{messageId}.",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

def setup(client):
	client.add_cog(Moderation(client))