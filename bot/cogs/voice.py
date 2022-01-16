import asyncio, discord, math, time
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
from utils import find_object

class voice(commands.Cog, name = "Voice"):
	"""Voice Channel Commands"""

	def __init__(self, client):
		self.client = client
		self.muted_users = {}
		self.mute_check.start()

	def cog_unload(self):
		self.mute_check.stop()

	@tasks.loop(minutes = 1)
	async def mute_check(self):
		users_ids_to_remove = []
		for user_id in self.muted_users:
			if self.muted_users[user_id][0] < time.time():
				users_ids_to_remove.append(user_id)
		
		for user_id in users_ids_to_remove:
			guild = await find_object.find_guild(self.client, self.muted_users[user_id][1])
			user = await find_object.find_member(guild, user_id)
			await user.edit(mute = False)
			self.muted_users.pop(user_id)

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if before.channel and before.channel.type == discord.ChannelType.voice:
			if not before.channel.members and before.channel.user_limit != 0:
				await before.channel.edit(
					user_limit = 0,
					reason = "All users left voice channel."
				)

	@commands.command(aliases = ['limit'])
	@commands.guild_only()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def cap(self, ctx, capacity: int):
		"""Set a capacity limit on a voice channel.
		You must be in a voice channel to use this command."""

		voice_state = ctx.author.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			embed = discord.Embed(
				description = "❌ You must be connected to a voice channel to use this command.",
				colour = discord.Colour.red()
			)

		elif capacity < 0 or capacity > 99:
			embed = discord.Embed(
				description = "❌ You can only set the capacity between 0 (unlimited) and 99.",
				colour = discord.Colour.red()
			)

		else:
			await voice_state.channel.edit(
				user_limit = capacity,
				reason = "Voice channel user limit changed by user command."
			)
			if capacity == 0:
				embed = discord.Embed(
					description = f"✅ Successfully uncapped {voice_state.channel.mention}.",
					colour = discord.Colour.green()
				)
			else:
				embed = discord.Embed(
					description = f"✅ Successfully capped {voice_state.channel.mention} at {capacity} members.",
					colour = discord.Colour.green()
				)
		await ctx.send(embed = embed)

	@commands.command(name = "removeCap", aliases = ['unCap', 'unlimit'])
	@commands.guild_only()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def remove_cap(self, ctx):
		"""Remove a capacity limit on a voice channel. 
		You must be in a voice channel to use this command."""

		voice_state = ctx.author.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			embed = discord.Embed(
				description = "❌ You must be connected to a voice channel to use this command.",
				colour = discord.Colour.red()
			)
		elif voice_state.channel.user_limit == 0:
			embed = discord.Embed(
				description = "❌ There is no user limit on this channel.",
				colour = discord.Colour.red()
			)
		else:
			await voice_state.channel.edit(
				user_limit = 0,
				reason = "Voice channel user limit changed by user command."
			)
			embed = discord.Embed(
				description = f"✅ Successfully uncapped {voice_state.channel.mention}.",
				colour = discord.Colour.green()
			)
		await ctx.send(embed = embed)

	@commands.command(name = "voiceKick", aliases = ["vcKick"])
	@commands.guild_only()
	@commands.max_concurrency(1, commands.BucketType.guild)
	async def voice_kick(self, ctx, user: discord.Member):
		"""Vote kick someone out of a voice channel. 2/3 of connected members must vote in favour.
		You must be in a voice channel to use this command."""
		
		voice_state = ctx.author.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			await ctx.send("❌ You must be connected to a voice channel to use this command.")
		
		elif not user in voice_state.channel.members: 
			await ctx.send(f"❌ {user.mention} is not in your voice channel.")

		else:
			required_votes = max(math.floor(len(voice_state.channel.members) * (2/3)), 1)
			current_votes = 0
			users_voted = []
			expiration_datetime = datetime.now(timezone.utc) + timedelta(minutes = 5)

			bot_id = self.client.user.id
			vc_mention = voice_state.channel.mention

			embed = discord.Embed(
				description = f"React with ☑️ to votekick {user.mention} out of {vc_mention}.\n`{current_votes}/{required_votes}` required votes.",
				colour = discord.Colour.gold(),
				timestamp = expiration_datetime
			)
			embed.set_author(
				name = f"Votekick for {user.display_name}",
				icon_url = user.avatar_url
			)
			embed.set_footer(
				text = f"Created by {ctx.author.display_name} | Vote ends"
			)

			embed_dict = embed.to_dict()
			vote_message = await ctx.send(embed = embed)
			await vote_message.add_reaction("☑️")

			def validate_reaction(temp_reaction, temp_user):
				if temp_user.id == bot_id:
					return False
				return temp_reaction.message.id == vote_message.id and str(temp_reaction.emoji) == "☑️" and temp_user.voice and voice_state.channel.id == temp_user.voice.channel.id

			while True:
				try:
					exp_time = expiration_datetime.time()
					current_time = datetime.now(timezone.utc).time()
					expiration_secs = (exp_time.hour * 60 + exp_time.minute) * 60 + exp_time.second
					current_secs = (current_time.hour * 60 + current_time.minute) * 60 + current_time.second
					if expiration_secs - current_secs <= 0:
						raise asyncio.TimeoutError
					new_reaction, new_user = await self.client.wait_for("reaction_add", check = validate_reaction, timeout = (expiration_secs - current_secs))
					
				except asyncio.TimeoutError:
					embed_dict["description"] = f"❌ Failed to votekick {user.mention} out of {vc_mention}. Time limit reached.\n`{current_votes}/{required_votes}` required votes."
					embed_dict["color"] = 15158332 # discord.Colour.red()
					embed_dict["footer"]["text"] = f"Created by {ctx.author.display_name} | Vote ended"
					embed = discord.Embed.from_dict(embed_dict)
					await vote_message.edit(
						embed = embed
					)
					break

				else:
					if not new_user.id in users_voted:
						users_voted.append(new_user.id)
						current_votes += 1

						if current_votes == required_votes:
							await user.edit(
								voice_channel = None,
								reason = "User was votekicked."
							)

							embed_dict["description"] = f"✅ {user.mention} has been kicked from {vc_mention}.\n`{current_votes}/{required_votes}` required votes."
							embed_dict["color"] = 3066993 # discord.Colour.green()
							embed_dict["footer"]["text"] = f"Created by {ctx.author.display_name} | Vote ended"
							embed_dict["timestamp"] = datetime.isoformat(datetime.now(timezone.utc))
							embed = discord.Embed.from_dict(embed_dict)
							await vote_message.edit(
								embed = embed
							)
							break
						
						else:
							embed_dict["description"] = f"React with ☑️ to votekick {user.mention} out of {vc_mention}.\n`{current_votes}/{required_votes}` required votes."
							embed = discord.Embed.from_dict(embed_dict)
							await vote_message.edit(
								embed = embed
							)

	@commands.command(name = "voiceMute", aliases = ["vcMute"])
	@commands.guild_only()
	@commands.max_concurrency(3, commands.BucketType.guild)
	async def voice_mute(self, ctx, user: discord.Member, duration: int):
		"""Vote to mute someone in a voice channel for a given time. 2/3 of connected members must vote in favour.
		You must be in a voice channel to use this command."""

		voice_state = ctx.author.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			await ctx.send("❌ You must be connected to a voice channel to use this command.")
		
		elif not user in voice_state.channel.members: 
			await ctx.send(f"❌ {user.mention} is not in your voice channel.")

		elif duration > 60 or duration < 0:
			await ctx.send(f"❌ `{duration}` is not valid. Enter a number between `1-60` minutes.")

		else:
			required_votes = max(math.floor(len(voice_state.channel.members) * (2/3)), 1)
			current_votes = 0
			users_voted = []
			expiration_datetime = datetime.now(timezone.utc) + timedelta(minutes = 5)

			bot_id = self.client.user.id
			vc_mention = voice_state.channel.mention

			embed = discord.Embed(
				description = f"React with ☑️ to vote to mute {user.mention} in {vc_mention} for {duration} minutes.\n`{current_votes}/{required_votes}` required votes.",
				colour = discord.Colour.gold(),
				timestamp = expiration_datetime
			)
			embed.set_author(
				name = f"{duration} Minute Voice Mute for {user.display_name}",
				icon_url = user.avatar_url
			)
			embed.set_footer(
				text = f"Created by {ctx.author.display_name} | Vote ends"
			)

			embed_dict = embed.to_dict()
			vote_message = await ctx.send(embed = embed)
			await vote_message.add_reaction("☑️")

			def validate_reaction(temp_reaction, temp_user):
				if temp_user.id == bot_id:
					return False
				return temp_reaction.message.id == vote_message.id and str(temp_reaction.emoji) == "☑️" and temp_user.voice and voice_state.channel.id == temp_user.voice.channel.id

			while True:
				try:
					exp_time = expiration_datetime.time()
					current_time = datetime.now(timezone.utc).time()
					expiration_secs = (exp_time.hour * 60 + exp_time.minute) * 60 + exp_time.second
					current_secs = (current_time.hour * 60 + current_time.minute) * 60 + current_time.second
					if expiration_secs - current_secs <= 0:
						raise asyncio.TimeoutError
					new_reaction, new_user = await self.client.wait_for("reaction_add", check = validate_reaction, timeout = (expiration_secs - current_secs))
					
				except asyncio.TimeoutError:
					embed_dict["description"] = f"❌ Vote mute failed. Time limit reached.\n`{current_votes}/{required_votes}` required votes."
					embed_dict["color"] = 15158332 # discord.Colour.red()
					embed_dict["footer"]["text"] = f"Created by {ctx.author.display_name} | Vote ended"
					embed = discord.Embed.from_dict(embed_dict)
					await vote_message.edit(
						embed = embed
					)
					break

				else:
					if not new_user.id in users_voted:
						users_voted.append(new_user.id)
						current_votes += 1

						if current_votes == required_votes:
							await user.edit(
								mute = True,
								reason = "User was votemuted."
							)
							self.muted_users[user.id] = [time.time() + duration * 60, ctx.guild.id]

							embed_dict["description"] = f"✅ {user.mention} has been been muted in {vc_mention} for {duration} minutes.\n`{current_votes}/{required_votes}` required votes."
							embed_dict["color"] = 3066993 # discord.Colour.green()
							embed_dict["footer"]["text"] = f"Created by {ctx.author.display_name} | Vote ended"
							embed_dict["timestamp"] = datetime.isoformat(datetime.now(timezone.utc))
							embed = discord.Embed.from_dict(embed_dict)
							await vote_message.edit(
								embed = embed
							)
							break
						
						else:
							embed_dict["description"] = f"React with ☑️ to vote to mute {user.mention} in {vc_mention} for {duration} minutes.\n`{current_votes}/{required_votes}` required votes."
							embed = discord.Embed.from_dict(embed_dict)
							await vote_message.edit(
								embed = embed
							)

	@commands.command(name = "voiceUnmute", aliases = ["vcUnmute"])
	@commands.guild_only()
	@commands.max_concurrency(3, commands.BucketType.guild)
	async def voice_unmute(self, ctx, user: discord.Member):
		"""Vote to unmute someone in a voice channel. 2/3 of connected members must vote in favour.
		You must be in a voice channel to use this command."""

		voice_state = ctx.author.voice
		if voice_state == None or voice_state.channel.type != discord.ChannelType.voice:
			await ctx.send("❌ You must be connected to a voice channel to use this command.")
		
		elif not user in voice_state.channel.members: 
			await ctx.send(f"❌ {user.mention} is not in your voice channel.")

		else:
			required_votes = max(math.floor(len(voice_state.channel.members) * (2/3)), 1)
			current_votes = 0
			users_voted = []
			expiration_datetime = datetime.now(timezone.utc) + timedelta(minutes = 5)

			bot_id = self.client.user.id
			vc_mention = voice_state.channel.mention

			embed = discord.Embed(
				description = f"React with ☑️ to vote to unmute {user.mention} in {vc_mention}.\n`{current_votes}/{required_votes}` required votes.",
				colour = discord.Colour.gold(),
				timestamp = expiration_datetime
			)
			embed.set_author(
				name = f"Voice Unmute for {user.display_name}",
				icon_url = user.avatar_url
			)
			embed.set_footer(
				text = f"Created by {ctx.author.display_name} | Vote ends"
			)

			embed_dict = embed.to_dict()
			vote_message = await ctx.send(embed = embed)
			await vote_message.add_reaction("☑️")

			def validate_reaction(temp_reaction, temp_user):
				if temp_user.id == bot_id:
					return False
				return temp_reaction.message.id == vote_message.id and str(temp_reaction.emoji) == "☑️" and temp_user.voice and voice_state.channel.id == temp_user.voice.channel.id

			while True:
				try:
					exp_time = expiration_datetime.time()
					current_time = datetime.now(timezone.utc).time()
					expiration_secs = (exp_time.hour * 60 + exp_time.minute) * 60 + exp_time.second
					current_secs = (current_time.hour * 60 + current_time.minute) * 60 + current_time.second
					if expiration_secs - current_secs <= 0:
						raise asyncio.TimeoutError
					new_reaction, new_user = await self.client.wait_for("reaction_add", check = validate_reaction, timeout = (expiration_secs - current_secs))
					
				except asyncio.TimeoutError:
					embed_dict["description"] = f"❌ Unmute vote failed. Time limit reached.\n`{current_votes}/{required_votes}` required votes."
					embed_dict["color"] = 15158332 # discord.Colour.red()
					embed_dict["footer"]["text"] = f"Created by {ctx.author.display_name} | Vote ended"
					embed = discord.Embed.from_dict(embed_dict)
					await vote_message.edit(
						embed = embed
					)
					break

				else:
					if not new_user.id in users_voted:
						users_voted.append(new_user.id)
						current_votes += 1

						if current_votes == required_votes:
							await user.edit(
								mute = False,
								reason = "User was unmute voted."
							)

							if user.id in self.muted_users:
								self.muted_users.pop(user.id)

							embed_dict["description"] = f"✅ {user.mention} has been been unmuted in {vc_mention}.\n`{current_votes}/{required_votes}` required votes."
							embed_dict["color"] = 3066993 # discord.Colour.green()
							embed_dict["footer"]["text"] = f"Created by {ctx.author.display_name} | Vote ended"
							embed_dict["timestamp"] = datetime.isoformat(datetime.now(timezone.utc))
							embed = discord.Embed.from_dict(embed_dict)
							await vote_message.edit(
								embed = embed
							)
							break
						
						else:
							embed_dict["description"] = f"React with ☑️ to vote to unmute {user.mention} in {vc_mention}.\n`{current_votes}/{required_votes}` required votes."
							embed = discord.Embed.from_dict(embed_dict)
							await vote_message.edit(
								embed = embed
							)

def setup(client):
	client.add_cog(voice(client))
