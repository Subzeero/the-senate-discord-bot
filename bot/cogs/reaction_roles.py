import discord
from discord import app_commands
from discord.ext import commands
from database.db import Database as db
from utils import find_object, transformers

class reaction_roles(commands.Cog, name = "Reaction Roles"):
	"""Manage Reaction Roles."""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	cmd_group = app_commands.Group(
		name="reactionroles",
		description="Reaction Role Commands.",
		guild_only=(True),
		default_permissions=discord.Permissions(administrator=True)
	)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if payload.event_type != "REACTION_ADD" or payload.user_id == self.bot.user.id or not payload.guild_id:
			return

		guild_id = payload.guild_id
		message_id = payload.message_id
		
		guild_object = await find_object.find_guild(self.bot, guild_id)
		if not guild_object:
			return

		member_object = await find_object.find_member(guild_object, payload.user_id)
		if not member_object:
			return

		emoji_object = payload.emoji
		guild_data = await db.get_guild(guild_id)
		rr_data = None

		for data in guild_data["reaction_roles"]:
			if data["message_id"] == message_id and (data["unicode_emoji"] == str(emoji_object) or data["custom_emoji_id"] == emoji_object.id):
				rr_data = data
				break

		if rr_data:
			role_object = await find_object.find_role(guild_object, rr_data["role_id"])
			if role_object:
				await member_object.add_roles(role_object, reason = "Reaction Role")
			else:
				channel_object = await find_object.find_channel(self.bot, rr_data["channel_id"])
				try:
					await channel_object.send(f"Reaction Role on message {message_id} has failed.\nThe role with id: `{rr_data['role_id']}` could not be found.")
				except:
					pass

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if payload.event_type != "REACTION_REMOVE" or payload.user_id == self.bot.user.id or not payload.guild_id:
			return

		guild_id = payload.guild_id
		message_id = payload.message_id
		
		guild_object = await find_object.find_guild(self.bot, guild_id)
		if not guild_object:
			return

		member_object = await find_object.find_member(guild_object, payload.user_id)
		if not member_object:
			return

		emoji_object = payload.emoji
		guild_data = await db.get_guild(guild_id)
		rr_data = None

		for data in guild_data["reaction_roles"]:
			if data["message_id"] == message_id and (data["unicode_emoji"] == str(emoji_object) or data["custom_emoji_id"] == emoji_object.id):
				rr_data = data
				break

		try:
			role_object = await find_object.find_role(guild_object, rr_data["role_id"])
			await member_object.remove_roles(role_object, reason = "Reaction Role")
		except:
			pass

	@cmd_group.command(name="list")
	@app_commands.checks.cooldown(2, 10, key=lambda i: (i.guild_id))
	async def rr_list(self, interaction: discord.Interaction) -> None:
		"""List reaction roles."""

		await interaction.response.defer()

		guild_data = await db.get_guild(interaction.guild.id)

		embed = discord.Embed(colour=discord.Colour.gold())
		embed.set_author(name=f"Reaction Roles in {interaction.guild.id}", icon_url=interaction.guild.icon.url)

		if not guild_data["reaction_roles"]:
			embed.add_field(name="None!", value="Use `/reactionrole add` to add some.")
		else:
			for rr_id, rr_data in enumerate(guild_data["reaction_roles"]):
				if rr_data["unicode_emoji"]:
					emoji_object = rr_data["unicode_emoji"]
				else:
					emoji_object = await find_object.find_emoji(interaction.guild, rr_data["custom_emoji_id"])

				channel_object = await find_object.find_channel(self.bot, rr_data["channel_id"])
				role_object = await find_object.find_role(interaction.guild, rr_data["role_id"])

				channel_str = channel_object and channel_object.mention or f":warning: ({str(rr_data['channel_id'])})"
				emoji_str = emoji_object and str(emoji_object) or f":warning: ({str(rr_data['custom_emoji_id'])})"
				role_str = role_object and role_object.mention or f":warning: ({str(rr_data['role_id'])})"

				if channel_object:
					jump_url = f"https://discord.com/channels/{interaction.guild.id}/{channel_object.id}/{rr_data['message_id']}"
					embed_text = f"Channel: {channel_str}\nMessage ID: {rr_data['message_id']} [[Jump]]({jump_url})\nEmoji: {emoji_str}\nRole: {role_str}"
				else:
					embed_text = f"Channel: {channel_str}\nMessage ID: {rr_data['message_id']}\nEmoji: {emoji_str}\nRole: {role_str}"
				
				embed.add_field(
					name = f"Reaction Role ID: {rr_id}",
					value = embed_text
				)

		await interaction.followup.send(embed=embed)

	@cmd_group.command(name="create")
	@app_commands.checks.cooldown(2, 10, key=lambda i: (i.guild_id))
	@app_commands.describe(
		message="The message to react to.",
		emoji="The emoji to react with.",
		role="The role to add/remove."
	)
	async def rr_create(
		self,
		interaction: discord.Interaction,
		message: app_commands.Transform[discord.Message, transformers.MessageTransformer], 
		emoji: str,
		role: app_commands.Transform[discord.Role, transformers.RoleTransformer]
	) -> None:
		"""Create a new reaction role."""

		await interaction.response.defer()

		try:
			await message.add_reaction(emoji)
		except:
			return await interaction.followup.send(embed=discord.Embed(description=f"❌ Invalid emoji: `{emoji}`.", colour=discord.Colour.red()))

		guild_data = await db.get_guild(interaction.guild.id)

		is_unicode_emoij = isinstance(emoji, str)
		is_custom_emoji = isinstance(emoji, discord.Emoji)

		guild_data["reaction_roles"].append({
			"channel_id": message.channel.id,
			"message_id": message.id,
			"unicode_emoji": is_unicode_emoij and emoji or "",
			"custom_emoji_id": is_custom_emoji and emoji.id or 0,
			"role_id": role.id
		})

		await db.set_guild(interaction.guild.id, guild_data)

		embed = discord.Embed(title = "✅ Reaction Role Successfully Created!", colour = discord.Colour.green())

		embed.add_field(name = "ReactionRoleID: ", value = len(guild_data["reaction_roles"]) - 1, inline = False)
		embed.add_field(name = "Channel: ", value = message.channel.mention, inline = False)
		embed.add_field(name = "MessageId: ", value = message.id, inline = False)
		embed.add_field(name = "Emoji: ", value = str(emoji), inline = False)
		embed.add_field(name = "Role: ", value = role.mention, inline = False)

		await interaction.followup.send(embed=embed)

	@rr_create.autocomplete("role")
	async def send_autocomplete(self, interaction: discord.Interaction, current_role: str) -> list[app_commands.Choice[str]]:
		roles = interaction.guild.roles
		return [app_commands.Choice(name=role.name, value=role.name) for role in roles if current_role in role.name and role.name != "@everyone"][:25]

	@cmd_group.command(name="remove")
	@app_commands.checks.cooldown(2, 10, key=lambda i: (i.guild_id))
	@app_commands.describe(reaction_role_id="The reactionRoleID to remove.")
	@app_commands.rename(reaction_role_id="reactionroleid")
	async def rr_remove(
		self,
		interaction: discord.Interaction,
		reaction_role_id: int
	) -> None:
		"""Remove a reaction role."""

		await interaction.response.defer()

		guild_data = await db.get_guild(interaction.guild.id)
		if reaction_role_id < 0 and reaction_role_id >= len(guild_data["reaction_roles"]):
			return await interaction.followup.send(embed=discord.Embed(description=f"❌ Invalid reactionRoleID: `{reaction_role_id}`.", colour=discord.Colour.red()))

		rr_data = guild_data["reaction_roles"].pop(reaction_role_id)
		await db.set_guild(interaction.guild.id, guild_data)

		if rr_data["unicode_emoji"]:
			emoji_object = rr_data["unicode_emoji"]
		else:
			emoji_object = await find_object.find_emoji(interaction.guild, rr_data["custom_emoji_id"])

		role_object = await find_object.find_role(interaction.guild, rr_data["role_id"])
		channel_object = await find_object.find_channel(self.bot, rr_data["channel_id"])

		try:
			message_object = await channel_object.fetch_message(rr_data["message_id"])
			await message_object.remove_reaction(emoji_object, self.bot.user)
		except:
			pass

		embed = discord.Embed(
			title = "✅ Reaction Role Successfully Removed!",
			colour = discord.Colour.green()
		)

		embed.add_field(name = "ReactionRoleID: ", value = reaction_role_id, inline = False)
		embed.add_field(name = "Channel: ", value = channel_object and channel_object.mention or f":warning: ({str(rr_data['channel_id'])})", inline = False)
		embed.add_field(name = "MessageId: ", value = rr_data["message_id"], inline = False)
		embed.add_field(name = "Emoji: ", value = emoji_object and str(emoji_object) or f":warning: ({str(rr_data['custom_emoji_id'])})", inline = False)
		embed.add_field(name = "Role: ", value = role_object and role_object.mention or f":warning: ({str(rr_data['role_id'])})", inline = False)

		await interaction.followup.send(embed=embed)

	@rr_remove.autocomplete("reaction_role_id")
	async def send_autocomplete(self, interaction: discord.Interaction, current_RRID: str) -> list[app_commands.Choice[str]]:
		RRIDS = range(len((await db.get_guild(interaction.guild.id))["reaction_roles"]))
		return [app_commands.Choice(name=str(RRID), value=str(RRID)) for RRID in RRIDS if current_RRID in str(RRID)]

async def setup(bot: commands.Bot):
	await bot.add_cog(reaction_roles(bot))
