import datetime, discord, math, psutil
from discord.ext import commands

class random(commands.Cog, name = "Random"):
	"""Random commands."""

	def __init__(self, client):
		self.client = client
		self.start_time = datetime.datetime.now()

	@commands.command(aliases = ["ping", "statistics"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def stats(self, ctx):
		"""Get some stats about the bot."""

		message = await ctx.send("Gathering stats...")
		
		cpu = psutil.cpu_percent(interval = 1)
		memory = psutil.virtual_memory()
		latency = self.client.latency

		current_time = datetime.datetime.now()
		uptime = (current_time - self.start_time).total_seconds()

		embed = discord.Embed(title = "Global Statistics", colour = discord.Colour.gold())

		embed.set_author(name = self.client.user.name, icon_url = self.client.user.avatar_url)
		
		embed.add_field(name = "Total Servers", value = str(len(self.client.guilds)))
		embed.add_field(name = "Total Users", value = str(len(self.client.users)))
		embed.add_field(name = "Uptime", value = f"{math.floor(uptime / 86400)} days, {math.floor(uptime % 86400 / 3600)} hours, {math.floor(uptime % 3600 / 60)} minutes")
		embed.add_field(name = "CPU Usage", value = f"{round(cpu)}%")
		embed.add_field(name = "Memory Usage", value = f"{round((memory.total - memory.available) / math.pow(10, 9), 2)}GB / {round(memory.total / math.pow(10, 9), 2)}GB")
		embed.add_field(name = "Latency", value = f"{math.floor(latency * 1000)} ms")

		await message.edit(content = None, embed = embed)

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
	client.add_cog(random(client))
