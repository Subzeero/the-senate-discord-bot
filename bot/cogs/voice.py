import asyncio, discord, math, traceback
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from utils import converters, find_object, transformers

class VoteView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=180)
		self.votes = []
		
	async def on_timeout(self) -> None:
		self.vote_button.disabled = True

		desc = {
			"kick": "kicked",
			"mute": "muted",
			"unmute": "unmuted"
		}

		self.embed_dict["description"] = f"❌ {self.user.mention} was not {desc[self.vote_type]}: time limit reached."
		self.embed_dict["color"] = 15158332 # discord.Colour.red()
		self.embed_dict["footer"]["text"] = f"Created by {self.author.display_name} | Vote ended"
		embed = discord.Embed.from_dict(self.embed_dict)
		await self.message.edit(embed=embed, view=self)

	@discord.ui.button(label="Vote (-/-)", style=discord.ButtonStyle.primary)
	async def vote_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		user_id = interaction.user.id
		if user_id in self.votes:
			self.votes.remove(user_id)
			result_embed = discord.Embed(description="✅ Vote removed.", colour=discord.Colour.green())
		else:
			self.votes.append(user_id)
			result_embed = discord.Embed(description="✅ Vote counted.", colour=discord.Colour.green())
		await interaction.response.send_message(embed=result_embed, ephemeral=True)

		self.vote_button.label = f"Vote ({len(self.votes)}/{self.required_votes})"
		try:
			if len(self.votes) >= self.required_votes:
				self.stop()
				self.vote_button.disabled = True

				if self.vote_type == "kick":
					desc = f"✅ {self.user.mention} has been kicked from {self.vc_mention}."
				elif self.vote_type == "mute":
					desc = f"✅ {self.user.mention} has been muted in {self.vc_mention} for {self.readable_duration}."
				elif self.vote_type == "unmute":
					desc = f"✅ {self.user.mention} has been unmuted in {self.vc_mention}."

				self.embed_dict["description"] = desc
				self.embed_dict["color"] = 3066993 # discord.Colour.green()
				self.embed_dict["footer"]["text"] = f"Created by {self.author.display_name} | Vote ended"
				self.embed_dict["timestamp"] = datetime.isoformat(discord.utils.utcnow())
				embed = discord.Embed.from_dict(self.embed_dict)
				
				await self.message.edit(embed=embed, view=self)

				if self.vote_type == "kick":
					user = await self.user.edit(voice_channel=None, reason="User was vote-kicked.")
				elif self.vote_type == "mute":
					user = await self.user.edit(mute=True, reason="User was vote-muted.")
					self.muted_users[user.id] = [int(discord.utils.utcnow().timestamp()) + self.duration]
					if self.duration < 60:
						await asyncio.sleep(self.duration)
						self.muted_users.pop(user.id)
						await self.user.edit(mute=False, reason="Mute duration reached.")
				elif self.vote_type == "unmute":
					user = await self.user.edit(mute=False, reason="User was vote-unmuted.")
		except Exception as E:
			traceback.print_exception(type(E), E, E.__traceback__)
		else:
			await self.message.edit(view=self)

class voice(commands.Cog, name = "Voice"):
	"""Voice related commands."""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.muted_users = {}
		self.modified_channels = {}
		self.mute_check.start()

	def cog_unload(self):
		self.mute_check.stop()

	@tasks.loop(minutes = 1)
	async def mute_check(self):
		users_ids_to_remove = []
		for user_id in self.muted_users:
			if self.muted_users[user_id][0] < int(discord.utils.utcnow().timestamp()):
				users_ids_to_remove.append(user_id)
		
		for user_id in users_ids_to_remove:
			self.muted_users.pop(user_id)
			try:
				guild = await find_object.find_guild(self.bot, self.muted_users[user_id][1])
				user = await find_object.find_member(guild, user_id)
				await user.edit(mute=False, reason="Mute duration reached.")
			except:
				pass

	@commands.Cog.listener()
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		if before.channel and before.channel.type == discord.ChannelType.voice:
			if before.channel.id in self.modified_channels and not before.channel.members and before.channel.user_limit != 0:
				old_cap = self.modified_channels.pop(before.channel.id)
				await before.channel.edit(
					user_limit=old_cap,
					reason="All users left voice channel."
				)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(2, 10)
	@app_commands.describe(capacity="The number of members allowed in the voice channel.")
	async def cap(self, interaction: discord.Interaction, capacity: app_commands.Range[int, 0, 99]) -> None:
		"""Set a capacity limit on your connected voice channel."""

		await interaction.response.defer(thinking=True)

		voice_state = interaction.user.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			embed = discord.Embed(description="❌ You must be connected to a voice channel to use this command.", colour=discord.Colour.red())

		else:
			self.modified_channels[voice_state.channel.id] = voice_state.channel.user_limit
			await voice_state.channel.edit(user_limit=capacity, reason=f"Voice channel user limit changed by {interaction.user.display_name}'s command.")
			embed = discord.Embed(description=f"✅ Uncapped {voice_state.channel.mention}" if capacity == 0 else f"✅ Capped {voice_state.channel.mention} at `{capacity}` members.", colour=discord.Colour.green())
		
		await interaction.followup.send(embed=embed)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(2, 10)
	async def uncap(self, interaction: discord.Interaction) -> None:
		"""Remove a capacity limit on your connected voice channel."""

		await interaction.response.defer(thinking=True)

		voice_state = interaction.user.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			embed = discord.Embed(description="❌ You must be connected to a voice channel to use this command.", colour=discord.Colour.red())
		elif not voice_state.channel.id in self.modified_channels:
			embed = discord.Embed(description="⚠️ I have not set a cap on this voice channel.\n\nIf one exists, remove it in the Discord settings page.", colour=discord.Colour.yellow())
		else:
			old_cap = self.modified_channels.pop(voice_state.channel.id)
			await voice_state.channel.edit(user_limit=old_cap, reason=f"Voice channel user limit changed by {interaction.user.display_name}'s command.")
			embed = discord.Embed(description=f"✅ Uncapped {voice_state.channel.mention}", colour=discord.Colour.green())
		
		await interaction.followup.send(embed=embed)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id))
	@app_commands.describe(user="The user to kick.")
	async def voicekick(self, interaction: discord.Interaction, user: app_commands.Transform[discord.Member, transformers.MemberTransformer]) -> None:
		"""Vote to kick a user out of your connected voice channel. 2/3 required to vote in favour."""

		voice_state = interaction.user.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			return await interaction.response.send_message(embed=discord.Embed(description="❌ You must be connected to a voice channel to use this command.", colour=discord.Colour.red()), ephemeral=True)
		elif not user in voice_state.channel.members:
			return await interaction.response.send_message(embed=discord.Embed(description=f"❌ {user.mention} is not connected to {voice_state.channel.mention}.", colour=discord.Colour.red()), ephemeral=True)
		else:
			required_votes = max(math.floor(len(voice_state.channel.members) * (2/3)), 1)
			expiration_datetime = discord.utils.utcnow() + timedelta(minutes=3)

			embed = discord.Embed(description=f"Vote below to kick {user.mention} out of {voice_state.channel.mention}.", colour=discord.Colour.gold(), timestamp=expiration_datetime)
			embed.set_author(name=f"Disconnect {user.display_name} from Voice", icon_url=user.display_avatar.url)
			embed.set_footer(text=f"Created by {interaction.user.display_name} | Vote ends")
			embed_dict = embed.to_dict()

			vote_view = VoteView()
			vote_view.vote_type = "kick"

			vote_view.required_votes = required_votes
			vote_view.user = user
			vote_view.author = interaction.user
			vote_view.vc_mention = voice_state.channel.mention
			vote_view.embed_dict = embed_dict
			vote_view.vote_button.label = f"Vote (0/{required_votes})"

			await interaction.response.send_message(embed=embed, view=vote_view)
			vote_view.message = await interaction.original_response()
		
	@voicekick.autocomplete("user")
	async def voicekick_autocomplete(self, interaction: discord.Interaction, current_user: str) -> list[app_commands.Choice[str]]:
		if interaction.user.voice and interaction.user.voice.channel:
			return [app_commands.Choice(name=user.display_name, value=user.display_name) for user in interaction.user.voice.channel.members if current_user.lower() in user.name.lower() or current_user.lower() in user.display_name.lower()][:25]
		else:
			return []

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id))
	@app_commands.describe(user="The user to mute", duration="The mute duration in s, m, h, d.")
	async def voicemute(self, interaction: discord.Interaction, user: app_commands.Transform[discord.Member, transformers.MemberTransformer], duration: app_commands.Transform[int, transformers.RelativeTimeTransformer]) -> None:
		"""Vote to mute a user in your connected voice channel. 2/3 required to vote in favour."""

		voice_state = interaction.user.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			return await interaction.response.send_message(embed=discord.Embed(description="❌ You must be connected to a voice channel to use this command.", colour=discord.Colour.red()), ephemeral=True)
		elif not user in voice_state.channel.members:
			return await interaction.response.send_message(embed=discord.Embed(description=f"❌ {user.mention} is not connected to {voice_state.channel.mention}.", colour=discord.Colour.red()), ephemeral=True)
		elif duration > 2419200: # 28 days:
			return await interaction.response.send_message(embed=discord.Embed(description="❌ Maximum `duration` is 28 days.", colour=discord.Colour.red()), ephemeral=True)
		else:
			required_votes = max(math.floor(len(voice_state.channel.members) * (2/3)), 1)
			expiration_datetime = discord.utils.utcnow() + timedelta(minutes=3)
			readable_duration = converters.ToReadableTime(timedelta(seconds=duration))

			embed = discord.Embed(description=f"Vote below to mute {user.mention} in {voice_state.channel.mention} for {readable_duration}.", colour=discord.Colour.gold(), timestamp=expiration_datetime)
			embed.set_author(name=f"Mute {user.display_name} in Voice Chat", icon_url=user.display_avatar.url)
			embed.set_footer(text=f"Created by {interaction.user.display_name} | Vote ends")
			embed_dict = embed.to_dict()

			vote_view = VoteView()
			vote_view.vote_type = "mute"
			vote_view.duration = duration
			vote_view.readable_duration = readable_duration
			vote_view.muted_users = self.muted_users

			vote_view.required_votes = required_votes
			vote_view.user = user
			vote_view.author = interaction.user
			vote_view.vc_mention = voice_state.channel.mention
			vote_view.embed_dict = embed_dict
			vote_view.vote_button.label = f"Vote (0/{required_votes})"

			await interaction.response.send_message(embed=embed, view=vote_view)
			vote_view.message = await interaction.original_response()

	@voicemute.autocomplete("user")
	async def voicemute_autocomplete(self, interaction: discord.Interaction, current_user: str) -> list[app_commands.Choice[str]]:
		if interaction.user.voice and interaction.user.voice.channel:
			return [app_commands.Choice(name=user.display_name, value=user.display_name) for user in interaction.user.voice.channel.members if current_user.lower() in user.name.lower() or current_user.lower() in user.display_name.lower()][:25]
		else:
			return []

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id))
	@app_commands.describe(user="The user to unmute.")
	async def voiceunmute(self, interaction: discord.Interaction, user: app_commands.Transform[discord.Member, transformers.MemberTransformer]) -> None:
		"""Vote to unmute a user in your connected voice channel. 2/3 required to vote in favour."""

		voice_state = interaction.user.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			return await interaction.response.send_message(embed=discord.Embed(description="❌ You must be connected to a voice channel to use this command.", colour=discord.Colour.red()), ephemeral=True)
		elif not user in voice_state.channel.members:
			return await interaction.response.send_message(embed=discord.Embed(description=f"❌ {user.mention} is not connected to {voice_state.channel.mention}.", colour=discord.Colour.red()), ephemeral=True)
		else:
			required_votes = max(math.floor(len(voice_state.channel.members) * (2/3)), 1)
			expiration_datetime = discord.utils.utcnow() + timedelta(minutes=3)

			embed = discord.Embed(description=f"Vote below to ummute {user.mention} in {voice_state.channel.mention}.", colour=discord.Colour.gold(), timestamp=expiration_datetime)
			embed.set_author(name=f"Unmute {user.display_name} in Voice Chat", icon_url=user.display_avatar.url)
			embed.set_footer(text=f"Created by {interaction.user.display_name} | Vote ends")
			embed_dict = embed.to_dict()

			vote_view = VoteView()
			vote_view.vote_type = "unmute"
			vote_view.muted_users = self.muted_users

			vote_view.required_votes = required_votes
			vote_view.user = user
			vote_view.author = interaction.user
			vote_view.vc_mention = voice_state.channel.mention
			vote_view.embed_dict = embed_dict
			vote_view.vote_button.label = f"Vote (0/{required_votes})"

			await interaction.response.send_message(embed=embed, view=vote_view)
			vote_view.message = await interaction.original_response()

	@voiceunmute.autocomplete("user")
	async def voiceunmute_autocomplete(self, interaction: discord.Interaction, current_user: str) -> list[app_commands.Choice[str]]:
		if interaction.user.voice and interaction.user.voice.channel:
			return [app_commands.Choice(name=user.display_name, value=user.display_name) for user in interaction.user.voice.channel.members if current_user.lower() in user.name.lower() or current_user.lower() in user.display_name.lower()][:25]
		else:
			return []

async def setup(bot: commands.Bot):
	await bot.add_cog(voice(bot))
