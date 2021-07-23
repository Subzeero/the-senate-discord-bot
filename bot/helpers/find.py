import discord

async def find_guild(client, guild_id: int):
	guild = client.get_guild(guild_id)
	if guild:
		return guild
	else:
		try:
			guild = await client.fetch_guild(guild_id)
		except:
			pass
		return guild

async def find_user(client, user_id: int):
	user = client.get_user(user_id)
	if user:
		return user
	else:
		try:
			user = await client.fetch_user(user_id)
		except:
			pass
		return user

async def find_member(guild, member_id: int):
	member = guild.get_member(member_id)
	if member:
		return member
	else:
		try:
			member = await guild.fetch_member(member_id)
		except:
			pass
		return member

async def find_channel(client, channel_id: int):
	channel = client.get_channel(channel_id)
	if channel:
		return channel
	else:
		try:
			member = await client.fetch_channel(channel_id)
		except:
			pass
		return member

async def find_emoji(guild, emoji_id: int):
	emoji = discord.utils.find(lambda e: e.id == emoji_id, guild.emojis)
	if emoji:
		return emoji
	else:
		try:
			emoji = await guild.fetch_emoji(emoji_id)
		except:
			pass
		return emoji
