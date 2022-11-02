import discord
from discord import app_commands
from discord.ext import commands

class users(commands.Cog, name = "Users"):
	"""User-based commands."""

	def __init__(self, client):
		self.client = client

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988)) ## REMOVE ME
	@app_commands.checks.cooldown(2, 10)
	@app_commands.describe(user="The user to fetch (blank for yourself).")
	async def avatar(self, interaction: discord.Interaction, user: discord.User = None) -> None:
		"""Get a user's avatar image."""

		if not user:
			user = interaction.user

		embed = discord.Embed(colour=discord.Colour.gold())
		embed.set_author(name = f"{user.display_name}'s Avatar")
		embed.set_image(url=user.display_avatar.url)

		await interaction.response.send_message(embed=embed)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.guilds(discord.Object(id=831000735671123988)) ## REMOVE ME
	@app_commands.checks.cooldown(2, 10)
	@app_commands.describe(member="The member to fetch (blank for yourself).")
	async def user_permissions(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
		"""List the permissions of a given user."""

		if not member:
			member = interaction.member

		perms = "/n".join(perm for perm, value in member.guild_permissions if value)

		embed = discord.Embed(description=perms, colour=discord.Colour.gold())
		embed.set_author(icon_url=member.display_avatar.url, name=f"{member.mention}'s Permissions")
		
		await interaction.response.send_message(embed=embed)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.guilds(discord.Object(id=831000735671123988)) ## REMOVE ME
	@app_commands.checks.cooldown(2, 10)
	@app_commands.describe()
	async def user_roles(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
		"""List the roles of a given user."""

		if not member:
			member = interaction.user

		def sortPos(role: discord.Role):
			return role.position

		sorted_roles = sorted(member.roles, key=sortPos, reverse=True)
		sorted_roles = [role.mention for role in sorted_roles]
		roles_str = "\n".join(sorted_roles)

		embed = discord.Embed(colour=discord.Colour.gold())
		embed.set_author(icon_url=member.display_avatar.url, name=f"{str(member)}'s Roles in {interaction.guild.name}")
		embed.add_field(name = "\uFEFF", value = roles_str, inline = False)

		await interaction.response.send_message(embed=embed)

async def setup(client):
	await client.add_cog(users(client))
