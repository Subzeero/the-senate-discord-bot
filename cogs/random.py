import discord, math
from discord.ext import commands

class Random(commands.Cog):
	"""Random commands."""

	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def ping(self, ctx):
		"""Check the latency of the bot."""

		latency = str(math.floor(self.client.latency * 1000))

		await ctx.send("Pong! `(" + latency + " ms)`")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def senate(self, ctx):
		"""Declare supremacy."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/RfTq.gif")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def doggo(self, ctx):
		"""Happy doggo."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/xFa5.gif")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def dab(self, ctx):
		"""Dab on those haters."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/xU6p.gif")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def timer(self, ctx):
		"""Create a countdown timer."""

def setup(client):
	client.add_cog(Random(client))
