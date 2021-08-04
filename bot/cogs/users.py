import discord
from discord.ext import commands

class users(commands.Cog, name = "Users"):
	"""User-based commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["profile", "av"])
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def avatar(self, ctx, member: discord.Member = None):
		"""Get a user's avatar image."""

		if not member:
			member = ctx.author

		embed = discord.Embed(
			colour = member.colour
		)

		embed.set_author(name = f"{member.display_name}'s Avatar", icon_url = member.avatar_url)
		embed.set_image(url = member.avatar_url)

		await ctx.send(embed)

	@commands.command(name = "userPermissions", aliases = ["uperms", "userperms"])
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def user_permissions(self, ctx, member: discord.Member = None):
		"""List the permissions of a given user."""

		if not member:
			member = ctx.author

		perms = "\n".join(perm for perm, value in member.guild_permissions if value)

		embed = discord.Embed(
			title = "Permissions",
			colour = member.colour
		)

		embed.set_author(
			icon_url = member.avatar_url,
			name = str(member)
		)

		embed.add_field(
			name = "\uFEFF",
			value = perms,
			inline = False
		)

		await ctx.send(embed = embed)

def setup(client):
	client.add_cog(users(client))
