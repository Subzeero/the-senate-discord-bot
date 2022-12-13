import aiohttp, asyncio, discord, math, psutil
from discord import app_commands
from discord.ext import commands, tasks
from database.db import Database as db
from utils import transformers

class random(commands.Cog, name = "Random"):
	"""Random commands."""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

		self.start_time = discord.utils.utcnow()

	@tasks.loop(minutes=5)
	async def timer_check(self):
		current_time = discord.utils.utcnow().timestamp()
		bot_data = await db.get_bot()
		timers_to_remove = []
		
		for index, timer in enumerate(bot_data["timers"]):
			if (timer[0] - 300) < current_time:
				timers_to_remove.append(index)
				try:
					await asyncio.sleep(timer[0] - current_time)
					async with aiohttp.ClientSession() as session:
						webhook = discord.Webhook.from_url(timer[1], session=session)
						embed = discord.Embed(description=f"{timer[2]}, your timer has finished.", colour=discord.Colour.gold())
						embed.set_image(url="https://c.tenor.com/P2RRAeEPXs4AAAAC/judge-judy-double-time.gif")
						await webhook.send(embed=embed)
				except:
					pass
		
		if timers_to_remove:
			for removal_index in timers_to_remove:
				bot_data["timers"].pop(removal_index)
			await db.set_bot(bot_data)

	@app_commands.command()
	@app_commands.checks.cooldown(2, 10)
	async def stats(self, interaction: discord.Interaction) -> None:
		"""Get some stats about the bot."""

		await interaction.response.defer(thinking=True)

		cpu = psutil.cpu_percent(interval=0.5)
		memory = psutil.virtual_memory()
		memory_total_GB = memory.total / 2**30
		memory_available_GB = memory.available / 2**30
		latency = math.floor(self.bot.latency * 1000)

		current_time = discord.utils.utcnow()
		uptime = (current_time - self.start_time).total_seconds()
		uptime_days = math.floor(uptime / 86400)
		uptime_hours = math.floor(uptime % 86400 / 3600)
		uptime_minutes = math.floor(uptime % 3600 / 60)

		embed = discord.Embed(title="Global Statistics", colour=discord.Colour.gold())
		embed.add_field(name = "Total Servers", value = str(len(self.bot.guilds)))
		embed.add_field(name = "Total Users", value = str(len(self.bot.users)))
		embed.add_field(name = "Uptime", value = f"{uptime_days} days, {uptime_hours} hours, {uptime_minutes} minutes")
		embed.add_field(name = "CPU Usage", value = f"{round(cpu)}%")
		embed.add_field(name = "Memory Usage", value = "{:0.2f}GB / {:0.2f}GB".format(memory_total_GB - memory_available_GB, memory_total_GB))
		embed.add_field(name = "Latency", value = f"{latency} ms")

		if interaction.guild.icon:
			embed.set_thumbnail(url=interaction.guild.icon.url)

		await interaction.followup.send(embed=embed)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(2, 10)
	async def serverstats(self, interaction: discord.Interaction) -> None:
		"""Get some stats about your server."""

		embed = discord.Embed(title=f"Server Statistics for {interaction.guild.name}", colour=discord.Colour.gold())
		embed.add_field(name = "Members", value = str(interaction.guild.member_count or "⚠️"))
		embed.add_field(name = "Text Channels", value = str(len(interaction.guild.text_channels)))
		embed.add_field(name = "Voice Channels", value = str(len(interaction.guild.voice_channels)))
		embed.add_field(name = "Roles", value = str(len(interaction.guild.roles)))
		embed.add_field(name = "Nitro Boosts", value = str(interaction.guild.premium_subscription_count))
		embed.add_field(name = "Boost Level", value = str(interaction.guild.premium_tier))
		embed.add_field(name = "Emojis", value = f"{len(interaction.guild.emojis)}/{interaction.guild.emoji_limit}")
		embed.add_field(name = "Owner", value = interaction.guild.owner.mention if interaction.guild.owner else "⚠️")
		embed.add_field(name = "Guild ID", value = str(interaction.guild.id))

		if interaction.guild.icon:
			embed.set_thumbnail(url=interaction.guild.icon.url)

		await interaction.response.send_message(embed=embed)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(2, 10)
	async def serverfeatures(self, interaction: discord.Interaction) -> None:
		"""Get the special Discord Features of your server."""

		feature_list = interaction.guild.features
		if feature_list:
			feature_text = "".join([("- "+feature+"\n") for feature in feature_list])
			feature_text = feature_text[:-1]
		else:
			feature_text = "None!"

		embed = discord.Embed(title=f"Server Features of {interaction.guild.name}", description=feature_text, colour=discord.Colour.gold())
		if interaction.guild.icon:
			embed.set_thumbnail(url=interaction.guild.icon.url)

		await interaction.response.send_message(embed=embed)

	@commands.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def senate(self, ctx):
		"""Declare supremacy."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/RfTq.gif")

	@commands.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def doggo(self, ctx):
		"""Happy doggo."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/xFa5.gif")

	@commands.command()
	@commands.cooldown(2, 10, commands.BucketType.user)
	async def dab(self, ctx):
		"""Dab on those haters."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/xU6p.gif")

	@app_commands.command()
	@app_commands.checks.cooldown(2, 10)
	@app_commands.describe(relative_time="The countdown duration in s/m/h/d.", disable_followup="Disable the followup reply when the timer ends.")
	async def timer(self, interaction: discord.Interaction, relative_time: app_commands.Transform[int, transformers.RelativeTimeTransformer], disable_followup: bool = False) -> None:
		"""Create a Discord timer embed to countdown to a relative time.
		A followup notification will sent for timers under 30 days."""

		await interaction.response.defer(thinking=True)

		current_time = int(discord.utils.utcnow().timestamp())
		target_time = current_time + relative_time

		await interaction.followup.send(embed=discord.Embed(description=f"ℹ️ A timer has been set for <t:{target_time}:T> (<t:{target_time}:R>)", colour=discord.Colour.gold()))

		if relative_time <= 300:
			await asyncio.sleep(relative_time)
			embed = discord.Embed(description=f"{interaction.user.mention}, your timer has finished.", colour=discord.Colour.gold())
			embed.set_image(url="https://c.tenor.com/P2RRAeEPXs4AAAAC/judge-judy-double-time.gif")
			await interaction.followup.send(embed=embed)
		
		elif relative_time <= 2592000:
			bot_data = await db.get_bot()
			bot_data["timers"].append([target_time, interaction.followup.url, interaction.user.mention])
			await db.set_bot(bot_data)

async def setup(bot: commands.Bot):
	await bot.add_cog(random(bot))
