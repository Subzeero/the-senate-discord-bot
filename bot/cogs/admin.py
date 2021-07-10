import discord
from discord.ext import commands
import database as db
from helpers import checks, embeds

RoleConverter = commands.RoleConverter()

class Admin(commands.Cog):
	"""Server administrator commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["listAdminRoles", "listAdministratorRoles", "listModRoles", "listModeratorRoles", "adminRoles", "modRoles"])
	@commands.guild_only()
	@checks.isAdmin()
	async def listControlRoles(self, ctx):
		"""List the administrator and moderator roles used by the bot."""

		server_data = db.validate_server(ctx.guild.id)
		admin_roles = server_data["admin_roles"]
		mod_roles = server_data["mod_roles"]
		adminStr = ""
		modStr = ""

		if admin_roles:
			for role in admin_roles:
				adminStr = f"{adminStr}\n`{role}`"
		else:
			adminStr = "None!"

		if mod_roles:
			for role in mod_roles:
				modStr = f"{modStr}\n`{role}`"
		else:
			modStr = "None!"

		embed = embeds.customEmbed(
			authorName = f"Bot Control Roles in {ctx.guild.name}",
			authorIconURL = ctx.guild.icon_url
		)

		embed.add_field(
			name = "Administrator Roles",
			value = adminStr,
			inline = False
		)

		embed.add_field(
			name = "Moderator Roles",
			value = modStr,
			inline = False
		)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["addAdminRole"])
	@commands.guild_only()
	@checks.isAdmin()
	async def addAdministratorRole(self, ctx, newAdminRole):
		"""Grant a role (name or id) access to administrator commands."""

		role = await RoleConverter.convert(ctx, newAdminRole)

		server_data = db.validate_server(ctx.guild.id)

		try:
			int(newAdminRole)
		except:
			server_data["admin_roles"].append(str(role))
		else:
			server_data["admin_roles"].append(role.id)

		db.set_server(ctx.guild.id, server_data)

		embed = embeds.infoEmbed(
			desc = f"✅ Successfully set `{newAdminRole}` as an admin role.",
			author = ctx.author
		)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["removeAdminRole"])
	@commands.guild_only()
	@checks.isAdmin()
	async def removeAdministratorRole(self, ctx, adminRoleToRemove):
		"""Remove a role's (name or id) access to administrator commands."""

		server_data = db.validate_server(ctx.guild.id)

		try:
			int(adminRoleToRemove)
		except:
			pass

		try:
			server_data["admin_roles"].remove(adminRoleToRemove)
		except:
			embed = embeds.infoEmbed(
				desc = f"❌ `{adminRoleToRemove}` is not an admin role.",
				author = ctx.author
			)
			await ctx.send(embed = embed)
		else:
			db.set_server(ctx.guild.id, server_data)
			embed = embeds.infoEmbed(
				desc = f"✅ `{adminRoleToRemove}` is no longer an admin role.",
				author = ctx.author
			)
			await ctx.send(embed = embed)

	@commands.command(aliases = ["addModRole"])
	@commands.guild_only()
	@checks.isAdmin()
	async def addModeratorRole(self, ctx, newModRole):
		"""Grant a role (name or id) access to moderator commands."""

		role = await RoleConverter.convert(ctx, newModRole)

		server_data = db.validate_server(ctx.guild.id)

		try:
			int(newModRole)
		except:
			server_data["mod_roles"].append(str(role))
		else:
			server_data["mod_roles"].append(role.id)

		db.set_server(ctx.guild.id, server_data)

		embed = embeds.infoEmbed(
			desc = f"✅ Successfully set `{newModRole}` as an moderator role.",
			author = ctx.author
		)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["removeModRole"])
	@commands.guild_only()
	@checks.isAdmin()
	async def removeModeratorRole(self, ctx, modRoleToRemove):
		"""Remove a role's access to access admin commands."""

		server_data = db.validate_server(ctx.guild.id)

		try:
			int(modRoleToRemove)
		except:
			pass

		try:
			server_data["mod_roles"].remove(modRoleToRemove)
		except:
			embed = embeds.infoEmbed(
				desc = f"❌ `{modRoleToRemove}` is not an moderator role.",
				author = ctx.author
			)
			await ctx.send(embed = embed)
		else:
			db.set_server(ctx.guild.id, server_data)
			embed = embeds.infoEmbed(
				desc = f"✅ `{modRoleToRemove}` is no longer an moderator role.",
				author = ctx.author
			)
			await ctx.send(embed = embed)

	@commands.command()
	@commands.guild_only()
	@checks.isAdmin()
	async def changePrefix(self, ctx, newPrefix:str = None):
		"""Change the bot's prefix."""
		server_data = db.validate_server(ctx.guild.id)
		server_data["custom_prefix"] = newPrefix
		db.set_server(ctx.guild.id, server_data)

		prefix = await self.client.get_prefix(ctx.message)
		await ctx.send(f"✅ prefix set to `{prefix}`.")

	@commands.command(aliases = ["say"])
	@commands.guild_only()
	@checks.isAdmin()
	async def echo(self, ctx, *, content:str):
		"""Echo a message back from the bot."""

		await ctx.message.delete()
		await ctx.send(content)

	@commands.command(aliases = ["edit"])
	@commands.guild_only()
	@checks.isAdmin()
	async def editMessage(self, ctx, messageID:int, newContent:str):
		"""Edit a message from the bot."""

		await ctx.message.delete()

		message = await ctx.fetch_message(messageID)

		if message.author.id == self.user.id:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		await message.edit(content = newContent, embed = None)

	@commands.command(aliases = ["sayembed"])
	@commands.guild_only()
	@checks.isAdmin()
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
	@checks.isAdmin()
	async def editEmbedMessage(self, ctx, messageID:int, *, newContent:str):
		"""Edit a message with an embed."""

		await ctx.message.delete()

		try:
			message = await ctx.fetch_message(messageID)
		except discord.NotFound:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		if message.author.id == self.user.id:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		embed = discord.Embed(
			description = newContent,
			colour = discord.Colour.gold()
		)

		await message.edit(content = None, embed = embed)

def setup(client):
	client.add_cog(Admin(client))
