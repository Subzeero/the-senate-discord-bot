import discord, asyncio
from discord import app_commands
from discord.ext import commands
from database.db import Database as db
from utils import debug, find_object

blockedRoleNames = ["moderator", "dj", "access", "hacker"]

class roles(commands.Cog, name = "Roles"):
	"""Role-related commands."""

	def __init__(self, client):
		self.client = client

	def debug_check(ctx):
		if not ctx.guild:
			return False

		debug_data = debug.get_debug_data()
		return ctx.guild.id in debug_data["testing_guilds"] or ctx.channel.id in debug_data["role_channels"]

	@commands.command()
	@commands.check(debug_check)
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
		roleList = []

		for role in sortedRoles:
			roleList.append(role.mention)
		
		roleStr = "\n".join(roleList)

		embed = discord.Embed(
			colour = discord.Colour.gold()
		)

		embed.set_author(
			name = f"Roles in {ctx.guild.name}",
			icon_url = ctx.guild.icon.url
		)

		embed = discord.Embed(colour=discord.Colour.gold())
		embed.set_author(name=f"Roles in {interaction.guild.name}", icon_url=interaction.guild.icon.url)
		embed.add_field(name="\uFEFF", value=role_str, inline=False)
			inline = False
		)

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
			description = role.mention,
			colour = role.colour
		)

		await interaction.response.send_message(embed=embed)
			name = "\uFEFF",
			value = perms,
			inline = False
		)

		await ctx.send(embed = embed)

async def setup(client):
	await client.add_cog(roles(client))
