import discord
from discord.ext import commands

class Moderation(commands.Cog):
	"""Moderation commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(name = "[WIP] purge")
	async def purge(self, ctx, var1, var2):
		"""Purge a number of messages."""

		await ctx.send("")

	@commands.command(aliases = ["r"])
	async def react(self, ctx, messageId:int, *reactions:str):
		"""Add reactions to the specified message."""

		await ctx.message.delete()

		message = await ctx.fetch_message(messageId)
		
		for reaction in reactions:
			await message.add_reaction(reaction)

		embed = discord.embed(
			title = "Success!",
			description = f"✅ Successfully added {reactions} to message #{messageId}",
			colour = discord.color.gold())

		await ctx.send(embed = embed)

def setup(client):
	client.add_cog(Moderation(client))