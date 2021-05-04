import discord
from discord.ext import commands
from database import db

class Admin(commands.Cog):
	"""Server administrator commands."""

	def __init__(self, client):
		self.client = client

	def checkAdminPerm(ctx):
		return ctx.channel.permissions_for(ctx.author).administrator

	def checkAdminRole(ctx):
		valid_roles = db.validate_server(ctx.guild.id)["admin_roles"]
		for role in ctx.author.roles:
			if str(role) in valid_roles or str(role.id) in valid_roles:
				return True
		return False

	@commands.command()
	@commands.guild_only()
	@commands.check_any(checkAdminPerm, checkAdminRole)
	async def listControlRoles(self, ctx):
		"""List the admin and mod roles used by the bot."""

		server_data = db.validate_server(ctx.guild.id)
		admin_roles = server_data["admin_roles"]
		mod_roles = server_data["moderator_roles"]

		embed = discord.Embed(
			colour = discord.Colour.gold()
		)

		embed.set_author(
			name = f"Bot Control Roles in {ctx.guild.name}",
			icon_url = ctx.guild.icon_url
		)

		embed.add_field(
			name = "Admin Roles",
			value = "\n".join(admin_roles)
		)

		embed.add_field(
			name = "Moderator Roles",
			value = "\n".join(mod_roles)
		)

		await ctx.send(embed = embed)

	@commands.command(aliases = ["say"])
	@commands.guild_only()
	@commands.check_any(checkAdminPerm, checkAdminRole)
	async def echo(self, ctx, *, content:str):
		"""Echo a message back from the bot."""

		await ctx.message.delete()
		await ctx.send(content)

	@commands.command(aliases = ["edit"])
	@commands.guild_only()
	@commands.check_any(checkAdminPerm, checkAdminRole)
	async def editMessage(self, ctx, messageID:int, newContent:str):
		"""Edit a message from the bot."""

		await ctx.message.delete()

		try:
			message = ctx.fetch_message(messageID)
		except discord.NotFound:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		if message.author.id == self.user.id:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		await message.edit(content = newContent, embed = None)

	@commands.command(aliases = ["sayembed"])
	@commands.guild_only()
	@commands.check_any(checkAdminPerm, checkAdminRole)
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
	@commands.check_any(checkAdminPerm, checkAdminRole)
	async def editEmbedMessage(self, ctx, messageID:int, *, newContent:str):
		"""Edit a message with an embed."""

		await ctx.message.delete()

		try:
			message = ctx.fetch_message(messageID)
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
