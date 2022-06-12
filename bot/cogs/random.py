import asyncio, datetime, discord, math, psutil
from discord.ext import commands
from utils import converters

class random(commands.Cog, name = "Random"):
	"""Random commands."""

	def __init__(self, client):
		self.client = client
		self.start_time = datetime.datetime.now()

	@commands.command(aliases = ["ping", "statistics", "uptime", "getStats"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def stats(self, ctx):
		"""Get some stats about the bot."""

		message = await ctx.send("Gathering stats...")
		
		cpu = psutil.cpu_percent(interval = 1)
		memory = psutil.virtual_memory()
		memory_total_GB = memory.total / 2**30
		memory_available_GB = memory.available / 2**30
		latency = math.floor(self.client.latency * 1000)

		current_time = datetime.datetime.now()
		uptime = (current_time - self.start_time).total_seconds()
		uptime_days = math.floor(uptime / 86400)
		uptime_hours = math.floor(uptime % 86400 / 3600)
		uptime_minutes = math.floor(uptime % 3600 / 60)

		embed = discord.Embed(title = "Global Statistics", colour = discord.Colour.gold())

		embed.set_author(name = self.client.user.name, icon_url = self.client.user.avatar_url)
		
		embed.add_field(name = "Total Servers", value = str(len(self.client.guilds)))
		embed.add_field(name = "Total Users", value = str(len(self.client.users)))
		embed.add_field(name = "Uptime", value = f"{uptime_days} days, {uptime_hours} hours, {uptime_minutes} minutes")
		embed.add_field(name = "CPU Usage", value = f"{round(cpu)}%")
		embed.add_field(name = "Memory Usage", value = "{:0.2f}GB / {:0.2f}GB".format(memory_total_GB - memory_available_GB, memory_total_GB))
		embed.add_field(name = "Latency", value = f"{latency} ms")

		await message.edit(content = None, embed = embed)

	@commands.command(aliases = ["serverStatistics", "getServerStats", "serverInfo"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.guild_only()
	async def serverStats(self, ctx):
		"""Get some stats about your server."""

		embed = discord.Embed(colour = discord.Colour.gold(), timestamp = ctx.guild.created_at)
		embed.set_author(name = f"Server Statistics for {ctx.guild.name}", icon_url = ctx.guild.icon_url)

		embed.add_field(name = "Members", value = str(ctx.guild.member_count))
		embed.add_field(name = "Text Channels", value = str(len(ctx.guild.text_channels)))
		embed.add_field(name = "Voice Channels", value = str(len(ctx.guild.voice_channels)))
		embed.add_field(name = "Roles", value = str(len(ctx.guild.roles)))
		embed.add_field(name = "Nitro Boosts", value = str(ctx.guild.premium_subscription_count))
		embed.add_field(name = "Boost Level", value = str(ctx.guild.premium_tier))
		embed.add_field(name = "Emoji Limit", value = str(ctx.guild.emoji_limit))
		embed.add_field(name = "Owner", value = f"<@!{str(ctx.guild.owner_id)}>")
		embed.add_field(name = "Guild ID", value = str(ctx.guild.id))

		embed.set_footer(text = "Created at ")

		await ctx.send(embed = embed)

	@commands.command(aliases = ["getServerFeatures"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.guild_only()
	async def serverFeatures(self, ctx):
		"""Get the Discord Features of your server."""

		feature_list = ctx.guild.features
		feature_text = ""
		if feature_list:
			for feature in feature_list:
				feature_text = feature_text + f"- {feature}\n"
			feature_text = feature_text[:-1]
		else:
			feature_text = "None"

		embed = discord.Embed(description = feature_text, colour = discord.Colour.gold())
		embed.set_author(name = f"Server Features of {ctx.guild.name}", icon_url=ctx.guild.icon_url)

		await ctx.send(embed = embed)

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
	@commands.max_concurrency(3, commands.BucketType.user)
	async def timer(self, ctx, *, relativeTime: converters.TimeConverter):
		"""Create a Discord rich-embed to countdown to a relative time. 
		An ending notification will be sent for timers under six hours."""

		unix = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
		target = unix + relativeTime
		timestamp_relative = f"<t:{target}:R>"
		timestamp_exact = f"<t:{target}:T>"
		await ctx.send(f"A timer has been set for {timestamp_exact}.\nThat is {timestamp_relative}.")

		if relativeTime <= 60 * 60 * 6:
			await asyncio.sleep(relativeTime)
			await ctx.message.reply(content = "https://tenor.com/FUGa.gif")

def setup(client):
	client.add_cog(random(client))
