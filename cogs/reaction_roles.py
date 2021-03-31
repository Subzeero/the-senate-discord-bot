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

		# if len()

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

		server_data[serverId]["reaction_roles"][name] = {
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
	async def removeReactionRole(self, ctx):
		"""Remove a reaction role."""

		await ctx.message.delete()
		await ctx.send("https://tenor.com/RfTq.gif")

def setup(client):
	client.add_cog(ReactionRoles(client))