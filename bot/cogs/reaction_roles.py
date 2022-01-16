import discord
from discord.ext import commands
from typing import Union
from database.db import Database as db
from utils import checks, converters, find_object

class reaction_roles(commands.Cog, name = "Reaction Roles"):
	"""Random commands."""

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if payload.event_type != "REACTION_ADD" or payload.user_id == self.client.user.id or not payload.guild_id:
			return

		guild_id = payload.guild_id
		message_id = payload.message_id
		
		guild_object = await find_object.find_guild(self.client, guild_id)
		if not guild_object:
			return

		member_object = await find_object.find_member(guild_object, payload.user_id)
		if not member_object:
			return

		emoji_object = payload.emoji
		guild_data = db.get_guild(guild_id)
		rr_data = None

		for data in guild_data["reaction_roles"]:
			if data["message_id"] == message_id and (data["unicode_emoji"] == str(emoji_object) or data["custom_emoji_id"] == emoji_object.id):
				rr_data = data
				break

		if rr_data:
			role_object = await find_object.find_role(guild_object, rr_data["role_id"])
			if role_object:
				await member_object.add_roles(role_object, reason = "Reaction Role")
			else:
				channel_object = await find_object.find_channel(self.client, rr_data["channel_id"])
				try:
					await channel_object.send(f"Reaction Role on message {message_id} has failed.\nThe role with id: `{rr_data['role_id']}` could not be found.")
				except:
					pass

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if payload.event_type != "REACTION_REMOVE" or payload.user_id == self.client.user.id or not payload.guild_id:
			return

		guild_id = payload.guild_id
		message_id = payload.message_id
		
		guild_object = await find_object.find_guild(self.client, guild_id)
		if not guild_object:
			return

		member_object = await find_object.find_member(guild_object, payload.user_id)
		if not member_object:
			return

		emoji_object = payload.emoji
		guild_data = db.get_guild(guild_id)
		rr_data = None

		for data in guild_data["reaction_roles"]:
			if data["message_id"] == message_id and (data["unicode_emoji"] == str(emoji_object) or data["custom_emoji_id"] == emoji_object.id):
				rr_data = data
				break

		try:
			role_object = await find_object.find_role(guild_object, rr_data["role_id"])
			await member_object.remove_roles(role_object, reason = "Reaction Role")
		except:
			pass

	@commands.command(aliases = ["reactionRoles"])
	@commands.guild_only()
	@commands.cooldown(1, 10, commands.BucketType.guild)
	@commands.check_any(checks.is_mod(), checks.is_admin())
	async def listReactionRoles(self, ctx):
		"""List all of the reaction roles."""

		guild_id = ctx.guild.id
		guild_data = db.get_guild(guild_id)

		if not guild_data["reaction_roles"]:
			embed = discord.Embed(
				description = "None!",
				colour = discord.Colour.gold()
			)
		else:
			embed = discord.Embed(
				colour = discord.Colour.gold()
			)

		embed.set_author(
			name = f"Reaction Roles in {ctx.guild.name}",
			icon_url = ctx.guild.icon_url
		)

		for rr_id, rr_data in enumerate(guild_data["reaction_roles"]):
			if rr_data["unicode_emoji"]:
				emoji_object = rr_data["unicode_emoji"]
			else:
				emoji_object = await find_object.find_emoji(ctx.guild, rr_data["custom_emoji_id"])

			channel_object = await find_object.find_channel(self.client, rr_data["channel_id"])
			role_object = await find_object.find_role(ctx.guild, rr_data["role_id"])

			channel_str = channel_object and channel_object.mention or f":warning: ({str(rr_data['channel_id'])})"
			emoji_str = emoji_object and str(emoji_object) or f":warning: ({str(rr_data['custom_emoji_id'])})"
			role_str = role_object and role_object.mention or f":warning: ({str(rr_data['role_id'])})"
			
			embed.add_field(
				name = f"Reaction Role ID: {rr_id}",
				value = f"Channel: {channel_str}\nMessage ID: {rr_data['message_id']}\nEmoji: {emoji_str}\nRole: {role_str}"
			)

		await ctx.send(embed=embed)

	@commands.command(aliases = ["createreactionrole", "addreactionrole"])
	@commands.guild_only()
	@commands.is_owner()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def newReactionRole(self, ctx, channel: discord.TextChannel, message_id: int, emoji: Union[discord.Emoji, converters.UnicodeEmojiConverter], role: discord.Role):
		"""Create a reaction role."""

		try:
			message = await channel.fetch_message(message_id)
		except discord.HTTPException:
			await ctx.send(f"❌ `{message_id}` is not a valid Message ID.")
			return

		await message.add_reaction(emoji)

		guild_id = ctx.guild.id
		guild_data = db.get_guild(guild_id)

		is_unicode_emoij = isinstance(emoji, str)
		is_custom_emoji = isinstance(emoji, discord.Emoji)

		guild_data["reaction_roles"].append({
			"channel_id": channel.id,
			"message_id": message_id,
			"unicode_emoji": is_unicode_emoij and emoji or "",
			"custom_emoji_id": is_custom_emoji and emoji.id or 0,
			"role_id": role.id
		})

		db.set_guild(guild_id, guild_data)

		embed = discord.Embed(title = "✅ Reaction Role Successfully Created!", colour = discord.Colour.green())

		embed.add_field(name = "ReactionRoleID: ", value = len(guild_data["reaction_roles"]) - 1, inline = False)
		embed.add_field(name = "Channel: ", value = channel.mention, inline = False)
		embed.add_field(name = "MessageId: ", value = message_id, inline = False)
		embed.add_field(name = "Emoji: ", value = str(emoji), inline = False)
		embed.add_field(name = "Role: ", value = role.mention, inline = False)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["deletereactionrole"])
	@commands.guild_only()
	@commands.is_owner()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	async def removeReactionRole(self, ctx, reactionRoleId: int):
		"""Remove a reaction role."""

		guild_id = ctx.guild.id
		guild_data = db.get_guild(guild_id)

		try:
			guild_data["reaction_roles"][reactionRoleId]
		except ValueError:
			await ctx.send(f"❌ `{reactionRoleId}` is not a valid reaction role ID.")
			return

		rr_data = guild_data["reaction_roles"].pop(reactionRoleId)
		db.set_guild(guild_id, guild_data)

		if rr_data["unicode_emoji"]:
			emoji_object = rr_data["unicode_emoji"]
		else:
			emoji_object = await find_object.find_emoji(ctx.guild, rr_data["custom_emoji_id"])

		role_object = await find_object.find_role(ctx.guild, rr_data["role_id"])
		channel_object = await find_object.find_channel(self.client, rr_data["channel_id"])

		try:
			message_object = await channel_object.fetch_message(rr_data["message_id"])
			await message_object.remove_reaction(emoji_object, self.client.user)
		except:
			pass

		embed = discord.Embed(
			title = "✅ Reaction Role Successfully Removed!",
			colour = discord.Colour.green()
		)

		embed.add_field(name = "ReactionRoleID: ", value = reactionRoleId, inline = False)
		embed.add_field(name = "Channel: ", value = channel_object and channel_object.mention or f":warning: ({str(rr_data['channel_id'])})", inline = False)
		embed.add_field(name = "MessageId: ", value = rr_data["message_id"], inline = False)
		embed.add_field(name = "Emoji: ", value = emoji_object and str(emoji_object) or f":warning: ({str(rr_data['custom_emoji_id'])})", inline = False)
		embed.add_field(name = "Role: ", value = role_object and role_object.mention or f":warning: ({str(rr_data['role_id'])})", inline = False)

		await ctx.send(embed = embed)

def setup(client):
	client.add_cog(reaction_roles(client))
