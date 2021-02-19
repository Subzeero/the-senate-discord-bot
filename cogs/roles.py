import discord
from discord.ext import commands
from replit import db

blockedRoleNames = ["moderator", "dj", "access", "hacker"]

class Roles(commands.Cog):
	"""Role-related commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(name = "[WIP]")
	@commands.guild_only()
	async def changeRole(self, ctx, colourHex: str, *roleName: str):
		"""[WIP]"""
		pass

	@commands.command()
	@commands.guild_only()
	async def listroles(self, ctx):
		"""List all of the server's roles."""

		roles = await ctx.guild.fetch_roles()
		roleList = "\n".join(roles)

		embed = discord.embed(
			title = "Roles for:",
			description = ctx.guild.name,
			colour = discord.colour.gold()
		)

		embed.add_field(
			name = "\uFEFF",
			value = roleList
		)

		await ctx.send(embed = embed)
		
	@commands.command(name = "rolepermissions", aliases = ["roleperms"])
	@commands.guild_only()
	async def role_permissions(self, ctx, *, role: discord.Role):
		"""List the permissions of given roles."""

		perms = "\n".join(perm for perm, value in role.permissions if value)

		embed = discord.Embed(
			title = "Permissions for:",
			description = role.mention,
			colour = role.colour
		)

		embed.add_field(
			name = "\uFEFF",
			value = perms
		)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["listperms", "perms"])
	@commands.guild_only()
	async def permissions(self, ctx, *, member: discord.Member = None):
		"""List the permissions of given users."""

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
			value = perms
		)

		await ctx.send(embed = embed)


def setup(client):
	client.add_cog(Roles(client))