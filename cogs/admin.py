import discord, replit
from discord.ext import commands
from replit import db

class Admin(commands.Cog):
	"""Administrator commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["ssr", "sr"])
	async def suggestionReactions(self, ctx, toggle:bool = True):
		"""Toggle auto-reactions for #server-suggestions."""

		await ctx.message.delete()

		db["suggestionReactionsEnabled"] = toggle
		start = "Enabled" if toggle else "Disabled"
		
		await ctx.send("✅ " + start + " message reactions in #server-suggestions.", delete_after = 5)

	@commands.command(aliases = ["say"])
	async def echo(self, ctx, *, content:str):
		"""Echo a message back from the bot."""

		await ctx.message.delete()
		await ctx.send(content)

	@commands.command()
	@commands.is_owner()
	async def changeStatus(self, ctx, newStatus: str):
		"""Change the bot's status."""

		await self.client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = newStatus))

def setup(client):
	client.add_cog(Admin(client))