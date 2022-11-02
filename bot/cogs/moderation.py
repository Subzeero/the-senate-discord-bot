import discord, math, datetime
from discord import app_commands
from discord.ext import commands
from utils import converters, transformers

class moderation(commands.Cog, name = "Moderation"):
	"""Moderation commands."""

	def __init__(self, bot: commands.Bot):
		self.client = bot
	
	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id))
	@app_commands.default_permissions(manage_messages=True)
	@app_commands.describe(
		amount="The number of messages to purge.",
		start="The message to begin purging from.",
		end="The message to stop purging at.",
		user="Only purge messages from this user."
	)
	async def purge(
		self,
		interaction: discord.Interaction,
		amount: app_commands.Range[int, 1, 250] = None,
		start: app_commands.Transform[discord.Message, transformers.MessageTransformer] = None,
		end: app_commands.Transform[discord.Message, transformers.MessageTransformer] = None,
		user: app_commands.Transform[discord.Member, transformers.MemberTransformer] = None
	) -> None:
		"""Purge an amount of messages OR all messages between two selected ones."""

		await interaction.response.defer(thinking=True)
		original_msg = await interaction.original_response()
		
		if amount:
			running_total = 0

			def purge_check(msg):
				nonlocal running_total
				if running_total >= amount:
					return False
				if msg.id == original_msg.id:
					return False
				if user:
					if msg.author.id == user.id:
						running_total += 1
						return True
					else:
						return False
				else:
					running_total += 1
					return True

			while True:
				if running_total < amount:
					await interaction.channel.purge(limit=math.floor(amount * 0.5 + 10), check=purge_check)
				else:
					break

			embed = discord.Embed(description=f"✅ Successfully purged `{running_total}` messages", colour=discord.Colour.green())
			embed.set_footer(text="This will self destruct in 5 seconds.")
		
		elif start and end:
			if start.id < end.id:
				temp = start
				start = end
				end = temp

			running_total = 0
			running_m_id = start.id
			start_purged = False
			end_purged = False
			
			def purge_check(msg):
				nonlocal running_total, start_purged, end_purged, running_m_id
				running_m_id = msg.id
				if msg.id == original_msg.id:
					return False
				if msg.id <= start.id and msg.id >= end.id:
					if msg.id == start.id:
						start_purged = True
					elif msg.id == end.id:
						end_purged = True
					running_total += 1
					return True

			while not start_purged and not end_purged:
				if running_m_id < end.id:
					embed = discord.Embed(description="⚠️ Something weird happened and some messages may have been missed", colour=discord.Colour.yellow())
					embed.set_footer(text="This will self destruct in 5 seconds.")
					break

				await interaction.channel.purge(limit=25, check=purge_check)

				if running_total > 250:
					embed = discord.Embed(description="⚠️ Purge Cap Reached: `250` Messages", colour=discord.Colour.yellow())
					embed.set_footer(text="This will self destruct in 5 seconds.")
					break

			embed = discord.Embed(description=f"✅ Successfully purged `{running_total}` messages", colour=discord.Colour.green())
			embed.set_footer(text="This will self destruct in 5 seconds.")
		
		else:
			embed = discord.Embed(description="❌ You must provide either `amount` or both `start` and `end`.", colour=discord.Colour.red())

		response = await interaction.followup.send(embed=embed)
		await response.delete(delay=5)

	@purge.autocomplete("user")
	async def purge_autocomplete(self, interaction: discord.Interaction, current_user: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=user.display_name, value=user.display_name) for user in interaction.guild.members if current_user.lower() in user.name.lower() or current_user.lower() in user.display_name.lower()][:25]
	
	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(2, 10)
	@app_commands.default_permissions(moderate_members=True)
	@app_commands.describe(
		user="The user to timeout.",
		duration="The timeout duration in s/m/h/d (default 15m).",
		reason="The reason for the timeout."
	)
	async def mute(
		self,
		interaction: discord.Interaction,
		user: app_commands.Transform[discord.Member, transformers.MemberTransformer],
		duration: app_commands.Transform[int, transformers.RelativeTimeTransformer] = None,
		reason: str = None
	) -> None:
		"""Give the specified user a time out."""

		await interaction.response.defer(thinking=True)

		timeout_td = datetime.timedelta(seconds=duration if duration else 900)
		await user.timeout(timeout_td, reason=f"From {interaction.user.display_name}: {reason}." if reason else f"{interaction.user.display_name} provided no reason.")
		await interaction.followup.send(embed=discord.Embed(description=f"✅ {user.mention} has been put on timeout for `{converters.ToReadableTime(timeout_td)}` for reason `{reason if reason else 'not provided'}`.", colour=discord.Colour.green()))

	@mute.autocomplete("user")
	async def mute_autocomplete(self, interaction: discord.Interaction, current_user: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=user.display_name, value=user.display_name) for user in interaction.guild.members if current_user.lower() in user.name.lower() or current_user.lower() in user.display_name.lower()][:25]

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(2, 10)
	@app_commands.default_permissions(moderate_members=True)
	@app_commands.describe(
		user="The user to remove from a timeout.",
		reason="The reason for removing the timeout."
	)
	async def unmute(
		self,
		interaction: discord.Interaction,
		user: app_commands.Transform[discord.Member, transformers.MemberTransformer],
		reason: str = None
	) -> None:
		"""Remove the specified user from a time out."""

		await interaction.response.defer(thinking=True)

		await user.timeout(None, reason=f"From {interaction.user.display_name}: {reason}." if reason else f"{interaction.user.display_name} provided no reason.")

		await interaction.followup.send(embed=discord.Embed(description=f"✅ {user.mention} has been removed from a timeout for reason `{reason if reason else 'not provided'}`.", colour=discord.Colour.green()))

	@unmute.autocomplete("user")
	async def unmute_autocomplete(self, interaction: discord.Interaction, current_user: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=user.display_name, value=user.display_name) for user in interaction.guild.members if current_user.lower() in user.name.lower() or current_user.lower() in user.display_name.lower()][:25]

async def setup(bot: commands.Bot):
	await bot.add_cog(moderation(bot))
