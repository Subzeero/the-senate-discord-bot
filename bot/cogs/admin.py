import discord
from discord.ext import commands
from database.db import Database as db
from utils import checks, find_object

class admin(commands.Cog, name = "Admin"):
	"""Server administrator commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["listAdminRoles", "listAdministratorRoles", "listModRoles", "listModeratorRoles", "adminRoles", "modRoles", "controlRoles"])
	@commands.guild_only()
	@checks.is_admin()
	async def listControlRoles(self, ctx):
		"""List the administrator and moderator roles used by the bot."""

		message = await ctx.send("Working...")
		
		guild_data = db.get_guild(ctx.guild.id)
		admin_str = ""
		mod_str = ""
		admin_roles_to_remove = []
		mod_roles_to_remove = []

		if guild_data["admin_roles"]:
			for role_id in guild_data["admin_roles"]:
				role_object = await find_object.find_role(ctx.guild, role_id)
				if role_object:
					admin_str = f"{admin_str}\n{role_object.mention}"
				else:
					admin_roles_to_remove.append(role_id)
		else:
			admin_str = "None!"

		if guild_data["mod_roles"]:
			for role_id in guild_data["mod_roles"]:
				role_object = await find_object.find_role(ctx.guild, role_id)
				if role_object:
					mod_str = f"{mod_str}\n{role_object.mention}"
				else:
					mod_roles_to_remove.append(role_id)
		else:
			mod_str = "None!"

		embed = discord.Embed(colour = discord.Colour.gold())

		embed.set_author(
			name = f"Control Roles in {ctx.guild.name}",
			icon_url = ctx.guild.icon_url
		)

		embed.add_field(
			name = "Administrator Roles",
			value = admin_str,
			inline = False
		)

		embed.add_field(
			name = "Moderator Roles",
			value = mod_str,
			inline = False
		)

		if admin_roles_to_remove:
			remove_str = ""
			for role_id in admin_roles_to_remove:
				guild_data["admin_roles"].remove(role_id)
				remove_str = f"{remove_str}\n`{role_id}`"
			db.set_guild(ctx.guild.id, guild_data)

			embed.add_field(
				name = "⚠️ Important Notice",
				value = f"The following role IDs could be not be found in your server (possibly deleted):{remove_str}\nThey have been removed as admin roles.",
				inline = False
			)

		if mod_roles_to_remove:
			remove_str = ""
			for role_id in mod_roles_to_remove:
				guild_data["mod_roles"].remove(role_id)
				remove_str = f"{remove_str}\n`{role_id}`"
			db.set_guild(ctx.guild.id, guild_data)

			embed.add_field(
				name = "⚠️ Important Notice",
				value = f"The following role IDs could be not be found in your server (possibly deleted):{remove_str}\nThey have been removed as mod roles.",
				inline = False
			)

		await message.edit(content = None, embed = embed)

	@commands.command(aliases = ["addAdminRole", "newAdminRole", "newAdministratorRole"])
	@commands.guild_only()
	@checks.is_admin()
	async def addAdministratorRole(self, ctx, newAdminRole: discord.Role):
		"""Grant a role access to administrator commands."""

		guild_data = db.get_guild(ctx.guild.id)
		guild_data["admin_roles"].append(newAdminRole.id)

		db.set_guild(ctx.guild.id, guild_data)

		embed = discord.Embed(
			description = f"✅ Successfully set {newAdminRole.mention} as an admin role.",
			colour = discord.Colour.green()
		)
		
		embed.set_author(
			name = f"{ctx.author.name}#{ctx.author.discriminator}",
			icon_url = ctx.author.avatar_url
		)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["addModRole"])
	@commands.guild_only()
	@checks.is_admin()
	async def addModeratorRole(self, ctx, newModRole: discord.Role):
		"""Grant a role access to moderator commands."""

		guild_data = db.get_guild(ctx.guild.id)
		guild_data["mod_roles"].append(newModRole.id)

		db.set_guild(ctx.guild.id, guild_data)

		embed = discord.Embed(
			description = f"✅ Successfully set {newModRole.mention} as a mod role.",
			colour = discord.Colour.green()
		)
		
		embed.set_author(
			name = f"{ctx.author.name}#{ctx.author.discriminator}",
			icon_url = ctx.author.avatar_url
		)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["removeAdminRole"])
	@commands.guild_only()
	@checks.is_admin()
	async def removeAdministratorRole(self, ctx, adminRoleToRemove: discord.Role):
		"""Remove a role's access to administrator commands."""

		guild_data = db.get_guild(ctx.guild.id)
		if not adminRoleToRemove.id in guild_data["admin_roles"]:
			embed = discord.Embed(
				description = f"❌ {adminRoleToRemove.mention} is not an admin role.",
				colour = discord.Colour.red()
			)
			embed.set_author(
				name = f"{ctx.author.name}#{ctx.author.discriminator}",
				icon_url = ctx.author.avatar_url
			)

		else: 
			guild_data["admin_roles"].remove(adminRoleToRemove.id)
			db.set_guild(ctx.guild.id, guild_data)
			embed = discord.Embed(
				description = f"✅ {adminRoleToRemove.mention} is no longer an admin role.",
				colour = discord.Colour.green()
			)
			embed.set_author(
				name = f"{ctx.author.name}#{ctx.author.discriminator}",
				icon_url = ctx.author.avatar_url
			)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["removeModRole"])
	@commands.guild_only()
	@checks.is_admin()
	async def removeModeratorRole(self, ctx, modRoleToRemove: discord.Role):
		"""Remove a role's access to moderator commands."""

		guild_data = db.get_guild(ctx.guild.id)
		if not modRoleToRemove.id in guild_data["mod_roles"]:
			embed = discord.Embed(
				description = f"❌ {modRoleToRemove.mention} is not an mod role.",
				colour = discord.Colour.red()
			)
			embed.set_author(
				name = f"{ctx.author.name}#{ctx.author.discriminator}",
				icon_url = ctx.author.avatar_url
			)

		else: 
			guild_data["mod_roles"].remove(modRoleToRemove.id)
			db.set_guild(ctx.guild.id, guild_data)
			embed = discord.Embed(
				description = f"✅ {modRoleToRemove.mention} is no longer an mod role.",
				colour = discord.Colour.green()
			)
			embed.set_author(
				name = f"{ctx.author.name}#{ctx.author.discriminator}",
				icon_url = ctx.author.avatar_url
			)

		await ctx.send(embed = embed)

	@commands.command()
	@commands.guild_only()
	@checks.is_admin()
	async def changePrefix(self, ctx, newPrefix:str = None):
		"""Change the bot's prefix. Send nothing to reset to the default prefix."""
		guild_data = db.get_guild(ctx.guild.id)
		guild_data["custom_prefix"] = newPrefix
		db.set_guild(ctx.guild.id, guild_data)

		prefixes = await self.client.get_prefix(ctx.message)
		prefix_str = ""

		if isinstance(prefixes, list):
			for prefix in prefixes:
				if not str(self.client.user.id) in prefix:
					prefix_str = prefix
		elif isinstance(prefixes, str):
			prefix_str = prefixes

		embed = discord.Embed(
			description = f"My prefix in this server is now: `{prefix_str}`\nUsage: `{prefix_str}help` or `@{self.client.user.display_name} help`.",
			colour = discord.Colour.green()
		)

		if newPrefix:
			embed.set_author(name = "✅ Prefix Reset to Default!")
		else:
			embed.set_author(name = "✅ Prefix Changed!")

		await ctx.send(embed = embed)

	@commands.command(aliases = ["say"])
	@commands.guild_only()
	@checks.is_admin()
	async def echo(self, ctx, *, content:str):
		"""Echo a message back from the bot."""

		await ctx.message.delete()
		await ctx.send(content)

	@commands.command(aliases = ["edit"])
	@commands.guild_only()
	@checks.is_admin()
	async def editMessage(self, ctx, message:discord.Message, newContent:str):
		"""Edit a message from the bot."""

		await ctx.message.delete()
		await message.edit(content = newContent, embed = None)

	@commands.command(aliases = ["sayembed"])
	@commands.guild_only()
	@checks.is_admin()
	async def echoEmbed(self, ctx, channel:discord.TextChannel, *, content:str):
		"""Make an announcement."""

		embed = discord.Embed(
			description = content,
			colour = discord.Colour.gold()
		)

		await ctx.message.delete()
		await channel.send(embed = embed)

	@commands.command()
	@commands.guild_only()
	@checks.is_admin()
	async def editEmbedMessage(self, ctx, message:discord.Message, *, newContent:str):
		"""Edit a message with an embed."""

		await ctx.message.delete()

		embed = discord.Embed(
			description = newContent,
			colour = discord.Colour.gold()
		)

		await message.edit(content = None, embed = embed)

def setup(client):
	client.add_cog(admin(client))
