import discord, asyncio
from discord import app_commands
from discord.ext import commands
from database.db import Database as db
from utils import debug, find_object

blockedRoleNames = ["moderator", "dj", "access", "hacker"]

# class ChangeRoleDropdown(discord.ui.Select):
# 	def __init__(self):
# 		options = [
# 			discord.SelectOption(label="Role Name", description="", emoji="📝"),
# 			discord.SelectOption(label="Role Colour", description="", emoji="🎨")
# 		]

# 		super().__init__(placeholder="Role Name or Role Colour?", min_values=1, max_values=1, options=options)

class ChangeRoleErrorView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=180)

	async def on_timeout(self) -> None:
		pass
	
	@discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
	async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		self.stop()

		await interaction.response.send_modal(ChangeRolePrompt())

	@discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
	async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		self.stop()

		# self.continue_button.disabled = True
		# self.cancel_button.disabled = True
		# await self.message.edit(view=self)

class ChangeRolePrompt(discord.ui.Modal, title="Customize your Role"):
	def __init__(self, role_choice_type: str):
		self.role_choice_type = role_choice_type
		if role_choice_type == "both":
			self.new_name_value = discord.ui.TextInput(
				label="Enter your new role name:",
				required=True
			)
			self.new_colour_value = discord.ui.TextInput(
				label="Enter your new role colour:",
				required=True
			)

			self.add_item(self.new_name_value)
			self.add_item(self.new_colour_value)

		else:
			self.new_role_value = discord.ui.TextInput(
				label=f"Enter your new role {role_choice_type}:",
				required=True
			)
			self.add_item(self.new_role_value)

		super().__init__()

	async def on_submit(self, interaction: discord.Interaction) -> None:
		guild_data = await db.get_guild(interaction.guild.id)

		if self.role_choice_type == "both":
			colour_input = self.new_colour_value.value.strip()
			if not colour_input.startswith("#"):
				colour_input = "#" + colour_input
			
			try:
				ctx = interaction.client.get_context(interaction)
				colour_value = await commands.ColourConverter().convert(interaction, ctx)
			except commands.BadColourArgument:
				pass

			new_role = await interaction.guild.create_role(name=self.new_name_value.value, colour=colour_value, reason="Created by user command.")
			
			role_position = 1
			if guild_data["custom_roles"]["placement_role_id"]:
				positioning_role = await find_object.find_role(interaction.guild, guild_data["custom_roles"]["placement_role_id"])
				role_position = positioning_role - 1

			new_role = await new_role.edit(position=role_position, reason="Reorder the new user role.")
			await interaction.user.add_roles(new_role)

			guild_data["custom_roles"]["user_roles"][str(interaction.user.id)] = new_role.id
			await db.set_guild(interaction.guild.id, guild_data)

			await interaction.response.send_message(embed=discord.Embed(description=f"✅ Role Created: {new_role.mention}", colour=discord.Colour.green()))

		elif self.role_choice_type == "colour":
			pass

		elif self.role_choice_type == "name":
			user_role = await find_object.find_role(interaction.guild, guild_data["custom_roles"]["user_roles"][str(interaction.user.id)])
			if not user_role:
				return await interaction.response.send_message(embed=discord.Embed(description="❌ Unable to access your role; try again later.", colour=discord.Colour.red()))

			user_role = await user_role.edit(name=self.new_name_value.value)
			await interaction.response.send_message(embed=discord.Embed(description=f"✅ Role Updated: {user_role.mention}", colour=discord.Colour.green()))

	# async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
	# 	await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

	# 	# Make sure we know what the error actually is
	# 	traceback.print_tb(error.__traceback__)

class ChangeRoleStartView(discord.ui.View):
	def __init__():
		super.__init__(timeout=180)

	async def on_timeout(self) -> None:
		pass

	@discord.ui.button(label="Continue", style=discord.ButtonStyle.success)
	async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		if self.role_choice_type == "both":
			await interaction.response.send_modal()

class ChangeRoleChoice(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label="Role Name", description="", emoji="📝"),
			discord.SelectOption(label="Role Colour", description="", emoji="🎨")
		]

		super().__init__(placeholder="Choose one:", min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_modal(ChangeRolePrompt(self.values[0]))


class ChangeRoleChoiceView(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(ChangeRoleChoice())

class roles(commands.Cog, name = "Roles"):
	"""Role-related commands."""

	def __init__(self, client):
		self.client = client

	def debug_check():
		async def predicate(ctx: commands.Context):
			if not ctx.guild:
				return False

			debug_data = await debug.get_debug_data()
			return ctx.guild.id in debug_data["testing_guilds"] or ctx.channel.id in debug_data["role_channels"]
		return commands.check(predicate)

	# @app_commands.command()
	# @app_commands.guild_only()
	# @app_commands.guilds(discord.Object(id=831000735671123988)) ## REMOVE ME
	# @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id))
	# async def changerole(self, interaction: discord.Interaction) -> None:
	# 	"""Change your role name or colour."""

	# 	guild_data = await db.get_guild(interaction.guild.id)
	# 	if not str(interaction.user.id) in guild_data["custom_roles"]["user_roles"].keys():
	# 		# NEW USER
	# 		pass
	# 	else:
	# 		#EXISTING USER
	# 		role = await find_object.find_role(interaction.guild, guild_data["custom_roles"]["user_roles"][str(interaction.user.id)])
	# 		if not role:
	# 			return await interaction.response.send_message(embed=discord.Embed(description="❌ Unable to access your role; try again later.", colour=discord.Colour.red()))
			
	# 		embed = discord.Embed(description=f"Your existing role is {role.mention}. Do you want to change its name or colour?", colour=discord.Colour.gold())
	# 		await interaction.response.send_message(embed=embed,view=ChangeRoleChoiceView())

	@commands.command()
	@debug_check()
	@commands.max_concurrency(1, commands.BucketType.guild)
	async def changeRole(self, ctx):
		"""Change your role name and colour."""
		guild_data = db.get_guild(ctx.guild.id)
		messages_to_delete = [ctx.message]

		def validateMessage(message):
			return message.author == ctx.author

		if not str(ctx.author.id) in guild_data["custom_roles"]["user_roles"].keys():
			embed = discord.Embed(
				title = "Custom Role Configuration",
				description = "It looks like you don't have a custom role yet; let's create one!",
				colour = discord.Colour.gold()
			)
			embed.add_field(
				name = "Step 1) Role Name",
				value = "What do you want your role name to be? Type it out below and send it. ",
				inline = False
			)
			embed.set_author(
				name = ctx.author.name + "#" + ctx.author.discriminator,
				icon_url = ctx.author.display_avatar.url
			)
			embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

			messages_to_delete.append(await ctx.send(embed = embed))

			try:
				response1 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
				messages_to_delete.append(response1)
			except asyncio.TimeoutError:
				embed = discord.Embed(
					title = "Custom Role Configuration",
					description = "❌ Role creation cancelled: timeout reached.",
					colour = discord.Colour.gold()
				)

				embed.set_author(
					name = ctx.author.name + "#" + ctx.author.discriminator,
					icon_url = ctx.author.display_avatar.url
				)

				embed.set_footer(text = "This message will self-destruct in 5 minutes.")

				await ctx.send(embed = embed, delete_after = 300)
				await ctx.channel.delete_messages(messages_to_delete)
				return

			if response1.content.lower() == "cancel":
				embed = discord.Embed(
					title = "Custom Role Configuration",
					description = "❌ Role creation cancelled.",
					colour = discord.Colour.gold()
				)

				embed.set_author(
					name = ctx.author.name + "#" + ctx.author.discriminator,
					icon_url = ctx.author.display_avatar.url
				)

				embed.set_footer(text = "This message will self-destruct in 5 minutes.")

				await ctx.send(embed = embed, delete_after = 300)
				await ctx.channel.delete_messages(messages_to_delete)
				return
			
			else:
				while True:
					embed = discord.Embed(
						title = "Custom Role Configuration",
						description = f"Great, I've got `{response1.content}` as your role name. If that's not what you want type `cancel` and start over from the beginning.",
						colour = discord.Colour.gold()
					)
					embed.add_field(
						name = "Step 2) Role Colour",
						value = "What do you want your role colour to be? Go to the link: https://htmlcolorcodes.com/color-picker/ and find the HEX colour code (#00BD1A in the image below) for the colour you want. Paste the HEX code below and send it.",
						inline = False
					)
					embed.set_image(
						url = "https://i.imgur.com/DxmuP7P.png"
					)
					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.display_avatar.url
					)
					embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

					messages_to_delete.append(await ctx.send(embed = embed))

					try:
						response2 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
						messages_to_delete.append(response2)
					except asyncio.TimeoutError:
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role creation cancelled: timeout reached.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messages_to_delete)
						break

					if response2.content.lower() == "cancel":
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role creation cancelled.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messages_to_delete)
						break

					else:
						try:
							user_input = response2.content.strip()
							if not user_input.startswith("#"):
								user_input = "#" + user_input

							colourValue = await commands.ColourConverter().convert(ctx, user_input)
						except commands.BadColourArgument:
							embed = discord.Embed(
								title = "Custom Role Configuration",
								description = "❌ That's not a valid hex colour code.",
								colour = discord.Colour.gold()
							)
							embed.set_author(
								name = ctx.author.name + "#" + ctx.author.discriminator,
								icon_url = ctx.author.display_avatar.url
							)

							messages_to_delete.append(await ctx.send(embed = embed))
							continue
						
						newRole = await ctx.guild.create_role(
							name = response1.content,
							colour = colourValue,
							reason = "Created by user command."
						)

						role_position = 1
						if guild_data["custom_roles"]["placement_role_id"]:
							positioning_role = await find_object.find_role(ctx.guild, guild_data["custom_roles"]["placement_role_id"])
							role_position = positioning_role.position - 1

						newRole = await newRole.edit(
							position = role_position,
							reason = "Reorder the role created by user command."
						)

						await ctx.author.add_roles(newRole)

						new_data = db.get_guild(ctx.guild.id)
						new_data["custom_roles"]["user_roles"][str(ctx.author.id)] = newRole.id
						db.set_guild(ctx.guild.id, new_data)

						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = f"✅ Role created: {newRole.mention}",
							colour = discord.Colour.gold()
						)
						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						await ctx.send(embed = embed)
						await ctx.channel.delete_messages(messages_to_delete)
						break

		else:
			while True:
				embed = discord.Embed(
					title = "Custom Role Configuration",
					description = "It looks like you have an existing custom role; what do you want to modify?",
					colour = discord.Colour.gold()
				)
				embed.add_field(
					name = "1) Role Name",
					value = "Reply with `1` if you want to change the name of your role.",
					inline = False
				)

				embed.add_field(
					name = "2) Role Colour",
					value = "Reply with `2` if you want to change the colour of your role.",
					inline = False
				)

				embed.set_author(
					name = ctx.author.name + "#" + ctx.author.discriminator,
					icon_url = ctx.author.display_avatar.url
				)
				embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

				messages_to_delete.append(await ctx.send(embed = embed))

				try:
					response1 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
					messages_to_delete.append(response1)
				except asyncio.TimeoutError:
					embed = discord.Embed(
						title = "Custom Role Configuration",
						description = "❌ Role configuration cancelled: timeout reached.",
						colour = discord.Colour.gold()
					)

					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.display_avatar.url
					)

					embed.set_footer(text = "This message will self-destruct in 5 minutes.")

					await ctx.send(embed = embed, delete_after = 300)
					await ctx.channel.delete_messages(messages_to_delete)
					break

				if response1.content.lower() == "cancel":
					embed = discord.Embed(
						title = "Custom Role Configuration",
						description = "❌ Role configuration cancelled.",
						colour = discord.Colour.gold()
					)

					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.display_avatar.url
					)

					embed.set_footer(text = "This message will self-destruct in 5 minutes.")

					await ctx.send(embed = embed, delete_after = 300)
					await ctx.channel.delete_messages(messages_to_delete)
					break

				elif response1.content == "1":
					embed = discord.Embed(
						title = "Custom Role Configuration",
						colour = discord.Colour.gold()
					)
					embed.add_field(
						name = "1) Role Name",
						value = "What do you want your role name to be? Type it out below and send it. ",
						inline = False
					)
					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.display_avatar.url
					)
					embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

					messages_to_delete.append(await ctx.send(embed = embed))

					try:
						response2 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
						messages_to_delete.append(response2)
					except asyncio.TimeoutError:
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role configuration cancelled: timeout reached.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messages_to_delete)
						break

					if response2.content.lower() == "cancel":
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role configuration cancelled.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messages_to_delete)
						break

					else:
						userRoleId = guild_data["custom_roles"]["user_roles"][str(ctx.author.id)]
						userRole = await find_object.find_role(ctx.guild, userRoleId)

						if not userRole:
							await ctx.send("❌ Discord is being mean, please try again later.\n`ERR: ROLE NOT FOUND`")
							break

						userRole = await userRole.edit(
							name = response2.content
						)

						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = f"✅ Role name modified: {userRole.mention}",
							colour = discord.Colour.gold()
						)
						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						await ctx.send(embed = embed)
						await ctx.channel.delete_messages(messages_to_delete)
						break

				elif response1.content == "2":
					embed = discord.Embed(
						title = "Custom Role Configuration",
						colour = discord.Colour.gold()
					)
					embed.add_field(
						name = "2) Role Colour",
						value = "What do you want your role colour to be? Go to the link: https://htmlcolorcodes.com/color-picker/ and find the HEX colour code (#00BD1A in the image below) for the colour you want. Paste the HEX code below and send it.",
						inline = False
					)
					embed.set_image(
						url = "https://i.imgur.com/seUpcRU.png"
					)
					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.display_avatar.url
					)
					embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

					messages_to_delete.append(await ctx.send(embed = embed))

					try:
						response2 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
						messages_to_delete.append(response2)
					except asyncio.TimeoutError:
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role creation cancelled: timeout reached.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messages_to_delete)
						break

					if response2.content.lower() == "cancel":
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role creation cancelled.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messages_to_delete)
						break

					else:
						try:
							user_input = response2.content.strip()
							if not user_input.startswith("#"):
								user_input = "#" + user_input

							colourValue = await commands.ColourConverter().convert(ctx, user_input)
						except commands.BadColourArgument:
							embed	= discord.Embed(
								title = "Custom Role Configuration",
								description = "❌ That's not a valid hex colour code.",
								colour = discord.Colour.gold()
							)
							embed.set_author(
								name = ctx.author.name + "#" + ctx.author.discriminator,
								icon_url = ctx.author.display_avatar.url
							)

							messages_to_delete.append(await ctx.send(embed = embed))
							continue
							
						userRoleId = guild_data["custom_roles"]["user_roles"][str(ctx.author.id)]
						userRole = await find_object.find_role(ctx.guild, userRoleId)

						if not userRole:
							await ctx.send("❌ Discord is being mean, please try again later.\n`ERR: ROLE NOT FOUND`")
							break

						userRole = await userRole.edit(
							colour = colourValue
						)

						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = f"✅ Role colour modified: {userRole.mention}",
							colour = discord.Colour.gold()
						)
						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.display_avatar.url
						)

						await ctx.send(embed = embed)
						await ctx.channel.delete_messages(messages_to_delete)
						break

				else:
					embed = discord.Embed(
						title = "Custom Role Configuration",
						description = "❌ Invalid response; please try again.",
						colour = discord.Colour.gold()
					)
					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.display_avatar.url
					)

					messages_to_delete.append(await ctx.send(embed = embed))

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 10)
	async def roles(self, interaction: discord.Interaction) -> None:
		"""List all the roles in the server."""

		fetched_roles = await interaction.guild.fetch_roles()

		def sortPos(role: discord.Role) -> int:
			return role.position

		sorted_roles = sorted(fetched_roles, key=sortPos, reverse=True)
		role_str = "\n".join([role.mention for role in sorted_roles])

		embed = discord.Embed(colour=discord.Colour.gold())
		embed.set_author(name=f"Roles in {interaction.guild.name}", icon_url=interaction.guild.icon.url)
		embed.add_field(name="\uFEFF", value=role_str, inline=False)

		await interaction.response.send_message(embed=embed)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.checks.cooldown(2, 10)
	@app_commands.describe(role="A role to list the permissions of.")
	async def rolepermissions(self, interaction: discord.Interaction, role: discord.Role) -> None:
		"""List the permissions of a role."""

		perms = "\n".join(perm for perm, value in role.permissions if value)

		embed = discord.Embed(title="Permissions for:", description=role.mention, colour=role.colour)
		embed.add_field(name="\uFEFF", value=perms, inline=False)

		await interaction.response.send_message(embed=embed)


async def setup(client):
	await client.add_cog(roles(client))
