import discord, math
from discord.ext import commands

class Random(commands.Cog):
	"""Random commands."""

	def __init__(self, client):
		self.client = client

	@commands.command()
	async def ping(self, ctx):
		"""Check the latency of the bot."""

		latency = str(math.floor(self.client.latency * 1000))

		await ctx.send("Pong! `(" + latency + " ms)`")

	@commands.command()
	async def senate(self, ctx):
		"""Declare supremacy."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/RfTq.gif")

	@commands.command()
	async def doggo(self, ctx):
		"""Happy doggo."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/xFa5.gif")

def setup(client):
	client.add_cog(Random(client))