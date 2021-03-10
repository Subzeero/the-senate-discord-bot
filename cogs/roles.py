import discord
from discord.ext import commands
from replit import db

blockedRoleNames = ["moderator", "dj", "access", "hacker"]

class Roles(commands.Cog):
	"""Role-related commands."""

	def __init__(self, client):
		self.client = client

	def check_Server(ctx):
		if not ctx.guild:
			return False
		return ctx.guild.id == 745683100788457614

	@commands.command()
	@commands.check(check_Server)
	async def changeRole(self, ctx):
		"""[WIP]"""

		server_data = None
		serverId = ctx.guild.id
		userId = ctx.author.id

		if not "server_data" in db.keys():
			server_data = {}
			db["server_data"] = server_data
		else:
			server_data = db["server_data"]

		if not serverId in server_data:
			server_data[serverId] = {}

		if not "custom_roles" in server_data[serverId]:
			server_data[serverId]["custom_roles"] = {}

		if not userId in server_data[serverId]["custom_roles"]:
			embed = discord.Embed(
				title = "Custom Role Configuration",
				description = "Looks like you don't have a custom role yet; let's create one!",
				colour = discord.Colour.gold()
			)
			embed.add_field(
				name = "1) Role Name",
				value = "What do you want your role name to be? Type it out below and send it. ",
				inline = False
			)
			embed.set_author(
				name = ctx.author.name + "#" + ctx.author.discriminator,
				icon_url = ctx.author.avatar_url
			)
			embed.set_footer(text = "This message will self-destruct in 2 minutes if you don't reply.")

			await ctx.send(embed = embed)

		#serverRoles = await ctx.guild.fetch_roles()

	@commands.command()
	@commands.check(check_Server)
	async def listroles(self, ctx):
		"""List all of the server's roles."""

		fetchedRoles = await ctx.guild.fetch_roles()

		def sortPos(role):
			return role.position

		sortedRoles = sorted(fetchedRoles, key = sortPos, reverse = True)

		roleList = []

		for role in sortedRoles:
			roleList.append(role.mention)
		
		roleStr = "\n".join(roleList)

		embed = discord.Embed(
			title = f"Roles in {ctx.guild.name}",
			colour = discord.Colour.gold()
		)

		embed.add_field(
			name = "\uFEFF",
			value = roleStr
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