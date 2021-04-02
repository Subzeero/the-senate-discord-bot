import discord, replit
from discord.ext import commands
import database as db

class ReactionRoles(commands.Cog):
	"""Random commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["reactionRoles"])
	@commands.guild_only()
	@commands.is_owner()
	async def listReactionRoles(self, ctx):
		"""Remove a reaction role."""

		serverId = str(ctx.guild.id)
		server_data = db.validate_server(serverId)

		embed = discord.Embed(
			colour = discord.Colour.gold()
		)

		embed.set_author(
			name = f"Reaction Roles in {ctx.guild.name}",
			icon_url = ctx.guild.icon_url
		)

		for rrName, rrData in server_data["reaction_roles"].items():
			for emoji in ctx.guild.emojis:
				if emoji.id == rrData["emojiId"]:
					emojiObject = emoji

			roleObject = ctx.guild.get_role(rrData["roleId"])

			embed.add_field(
				name = rrName,
				value = f"Message ID: {rrData['messageId']}\nEmoji: {str(emojiObject)}\nRole: {roleObject.mention}"
			)

		await ctx.send(embed=embed)

	@commands.command(aliases = ["createreactionrole", "addreactionrole"])
	@commands.guild_only()
	@commands.is_owner()
	async def newReactionRole(self, ctx, messageId: int, emoji: discord.Emoji, role: discord.Role, *, name: str):
		"""Create a reaction role."""

		try:
			message = await ctx.fetch_message(messageId)
		except discord.HTTPException:
			await ctx.send(f"❌ `{messageId}` is not a valid messageId.")
			return

		await message.add_reaction(emoji)

		serverId = str(ctx.guild.id)
		server_data = db.validate_server(serverId)

		server_data["reaction_roles"][name] = {
			"messageId": messageId,
			"emojiId": emoji.id,
			"roleId": role.id
		}

		db.set_server(serverId, server_data)

		embed = discord.Embed(
			title = "✅ Reaction Role Successfully Created!",
			colour = discord.Colour.gold()
		)

		embed.add_field(name = "Name: ", value = name, inline = False)
		embed.add_field(name = "MessageId: ", value = messageId, inline = False)
		embed.add_field(name = "Emoji: ", value = emoji, inline = False)
		embed.add_field(name = "Role: ", value = role.mention, inline = False)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["deletereactionrole"])
	@commands.guild_only()
	@commands.is_owner()
	async def removeReactionRole(self, ctx, reactionRoleName: str):
		"""Remove a reaction role."""

		serverId = str(ctx.guild.id)
		server_data = db.validate_server(serverId)

		for name, reactionRoleData in server_data["reaction_roles"]:
			if name == reactionRoleName:
				print("Here")

def setup(client):
	client.add_cog(ReactionRoles(client))
