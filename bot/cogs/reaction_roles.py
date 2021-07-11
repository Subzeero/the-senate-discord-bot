import discord, emoji as emoji_lib, regex
from discord.ext import commands
from typing import Union
from database.db import Database as db

class ReactionRoles(commands.Cog):
	"""Random commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["reactionRoles"])
	@commands.guild_only()
	async def listReactionRoles(self, ctx):
		"""List all of the reaction roles."""

		serverId = ctx.guild.id
		server_data = db.get_server(serverId)

		if not server_data["reaction_roles"]:
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

		for rrId, rrData in enumerate(server_data["reaction_roles"]):
			if rrData["unicodeEmoji"]:
				emojiObject = rrData["unicodeEmoji"]

			else:
				for emoji in ctx.guild.emojis:
					if emoji.id == rrData["customEmojiId"]:
						emojiObject = emoji
						break

			roleObject = ctx.guild.get_role(rrData["roleId"])

			embed.add_field(
				name = f"ReactionRoleID: {rrId}",
				value = f"Message ID: {rrData['messageId']}\nEmoji: {str(emojiObject)}\nRole: {roleObject.mention}"
			)

		await ctx.send(embed=embed)

	@commands.command(aliases = ["createreactionrole", "addreactionrole"])
	@commands.guild_only()
	@commands.is_owner()
	async def newReactionRole(self, ctx, messageId: int, emoji: Union[discord.Emoji, str], role: discord.Role):
		"""Create a reaction role."""

		def validateEmoji(string):
			emojiData = regex.findall(r"\X", string)
			flagData = regex.findall(u"[\U0001F1E6-\U0001F1FF]", string)

			for word in emojiData:
				if any(character in emoji_lib.UNICODE_EMOJI["en"] for character in word):
					return word
			
			return flagData

		def validateCustomEmoji(string):
			return isinstance(string, discord.Emoji)
			
		isCustomEmoji = validateCustomEmoji(emoji)

		if not isCustomEmoji:
			isEmoji = validateEmoji(emoji)
		else:
			isEmoji = False

		if not isEmoji and not isCustomEmoji:
			await ctx.send(f"❌ `{emoji}` is not a valid emoji.")
			return

		try:
			message = await ctx.fetch_message(messageId)
		except discord.HTTPException:
			await ctx.send(f"❌ `{messageId}` is not a valid messageId.")
			return

		await message.add_reaction(emoji)

		serverId = ctx.guild.id
		server_data = db.get_server(serverId)

		server_data["reaction_roles"].append({
			"messageId": messageId,
			"unicodeEmoji": isEmoji and emoji or "",
			"customEmojiId": isCustomEmoji and emoji.id or 0,
			"roleId": role.id
		})

		db.set_server(serverId, server_data)

		embed = discord.Embed(
			title = "✅ Reaction Role Successfully Created!",
			colour = discord.Colour.gold()
		)

		embed.add_field(name = "ReactionRoleID: ", value = len(server_data["reaction_roles"]) - 1, inline = False)
		embed.add_field(name = "MessageId: ", value = messageId, inline = False)
		embed.add_field(name = "Emoji: ", value = emoji, inline = False)
		embed.add_field(name = "Role: ", value = role.mention, inline = False)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["deletereactionrole"])
	@commands.guild_only()
	@commands.is_owner()
	async def removeReactionRole(self, ctx, reactionRoleId: int):
		"""Remove a reaction role."""

		serverId = ctx.guild.id
		server_data = db.get_server(serverId)

		try:
			server_data["reaction_roles"][reactionRoleId]
		except ValueError:
			await ctx.send(f"❌ `{reactionRoleId}` is not a valid reaction role ID.")
			return

		rrData = server_data["reaction_roles"].pop(reactionRoleId)
		db.set_server(serverId, server_data)

		if rrData["unicodeEmoji"]:
			emojiObject = rrData["unicodeEmoji"]
		else:
			for emoji in ctx.guild.emojis:
				if emoji.id == rrData["customEmojiId"]:
					emojiObject = emoji

		roleObject = ctx.guild.get_role(rrData["roleId"])
		messageObject = None

		try:
			messageObject = await ctx.fetch_message(rrData["messageId"])
		except:
			None

		if not roleObject:
			await ctx.send(f"❌ Reaction Role removed from database; unable to find role with ID: {rrData['roleId']}.")
			return

		if not emojiObject:
			await ctx.send(f"❌ Reaction Role removed from database; unable to find emoji with ID: {rrData['customEmojiId']} or unicode: {rrData['unicodeEmoji']}.")
			return

		if messageObject:
			await messageObject.remove_reaction(emojiObject, self.client.user)

		embed = discord.Embed(
			title = "✅ Reaction Role Successfully Removed!",
			colour = discord.Colour.gold()
		)

		embed.add_field(name = "ReactionRoleID: ", value = reactionRoleId, inline = False)
		embed.add_field(name = "MessageId: ", value = rrData["messageId"], inline = False)
		embed.add_field(name = "Emoji: ", value = emojiObject, inline = False)
		embed.add_field(name = "Role: ", value = roleObject.mention, inline = False)

		await ctx.send(embed = embed)

def setup(client):
	client.add_cog(ReactionRoles(client))
