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

		embed.set_author(name = f"{member.display_name}'s Avatar", icon_url = member.display_avatar.url)
		embed.set_image(url = member.display_avatar.url)

		await ctx.send(embed = embed)

	@commands.command(name = "userPermissions", aliases = ["uperms", "userperms"])
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def user_permissions(self, ctx, member: discord.Member = None):
		"""List the permissions of a given user."""

		if not member:
			member = ctx.author

		perms = "\n".join(perm for perm, value in member.guild_permissions if value)

		embed = discord.Embed(
			description = perms,
			colour = member.colour
		)

		embed.set_author(
			icon_url = member.display_avatar.url,
			name = f"{str(member)}'s Permissions"
		)

		await ctx.send(embed = embed)

	@commands.command(name = "userRoles", aliases = ["uroles"])
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def user_roles(self, ctx, member: discord.Member = None):
		"""List the roles of a given user."""

		if not member:
			member = ctx.author

		def sortPos(role):
			return role.position

		sortedRoles = sorted(member.roles, key = sortPos, reverse = True)

		roleList = []

		for role in sortedRoles:
			roleList.append(role.mention)
		
		roleStr = "\n".join(roleList)

		embed = discord.Embed(
			colour = discord.Colour.gold()
		)

		embed.set_author(
			icon_url = member.display_avatar.url,
			name = f"{str(member)}'s Roles in {ctx.guild.name}"
		)

		embed.add_field(
			name = "\uFEFF",
			value = roleStr,
			inline = False
		)

		await ctx.send(embed = embed)

async def setup(client):
	await client.add_cog(users(client))
