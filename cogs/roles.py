import discord, asyncio
from discord.ext import commands
import database as db
roleChangeInProgress = False

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
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def changeRole(self, ctx):
		"""[WIP]"""

		global roleChangeInProgress
		if roleChangeInProgress:
			await ctx.send("Someone else is changing their role right now. Please try again later.")
			return
		roleChangeInProgress = True

		serverId = ctx.guild.id
		userId = ctx.author.id
		server_data = db.validate_server(serverId)
		messagesList = [ctx.message]

		def validateMessage(message):
			return message.author == ctx.author

		if not str(userId) in server_data["custom_roles"]:
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
				icon_url = ctx.author.avatar_url
			)
			embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

			messagesList.append(await ctx.send(embed = embed))

			try:
				response1 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
				messagesList.append(response1)
			except asyncio.TimeoutError:
				embed = discord.Embed(
					title = "Custom Role Configuration",
					description = "❌ Role creation cancelled: timeout reached.",
					colour = discord.Colour.gold()
				)

				embed.set_author(
					name = ctx.author.name + "#" + ctx.author.discriminator,
					icon_url = ctx.author.avatar_url
				)

				embed.set_footer(text = "This message will self-destruct in 5 minutes.")

				await ctx.send(embed = embed, delete_after = 300)
				await ctx.channel.delete_messages(messagesList)
				roleChangeInProgress = False
				return

			if response1.content == "cancel":
				embed = discord.Embed(
					title = "Custom Role Configuration",
					description = "❌ Role creation cancelled.",
					colour = discord.Colour.gold()
				)

				embed.set_author(
					name = ctx.author.name + "#" + ctx.author.discriminator,
					icon_url = ctx.author.avatar_url
				)

				embed.set_footer(text = "This message will self-destruct in 5 minutes.")

				await ctx.send(embed = embed, delete_after = 300)
				await ctx.channel.delete_messages(messagesList)
				roleChangeInProgress = False
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
						value = "What do you want your role colour to be? Go to the link: https://htmlcolorcodes.com/ and find the HEX colour code (#00BD1A in the image below) for the colour you want. Paste the HEX code below and send it.",
						inline = False
					)
					embed.set_image(
						url = "https://i.imgur.com/seUpcRU.png"
					)
					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.avatar_url
					)
					embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

					messagesList.append(await ctx.send(embed = embed))

					try:
						response2 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
						messagesList.append(response2)
					except asyncio.TimeoutError:
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role creation cancelled: timeout reached.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.avatar_url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messagesList)
						roleChangeInProgress = False
						break

					if response2.content == "cancel":
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role creation cancelled.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.avatar_url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messagesList)
						roleChangeInProgress = False
						break

					else:
						def isHex(input):
							def removePrefix(input):
								if input.startswith("#"):
									return input[1:]
								else:
									return input
							
							formattedInput = removePrefix(input)
							
							if len(formattedInput) != 6:
								return False

							try:
								return int(removePrefix(input), 16)
							except ValueError:
								return False

						colourValue = isHex(response2.content)
						
						if colourValue:
							hackerRole = ctx.guild.get_role(745863515998519360)
							if not hackerRole:
								roleChangeInProgress = False
								await ctx.send("❌ Discord is being mean, please try again later.")
								break

							newRole = await ctx.guild.create_role(
								name = response1.content,
								colour = colourValue,
								reason = "Created by user command."
							)

							await newRole.edit(
								position = hackerRole.position - 1,
								reason = "Reorder the role created by user command."
							)

							await ctx.author.add_roles(newRole)

							server_data = db.validate_server(serverId)
							server_data["custom_roles"][str(userId)] = newRole.id
							db.set_server(serverId, server_data)

							embed = discord.Embed(
								title = "Custom Role Configuration",
								description = f"✅ Role created: {newRole.mention}",
								colour = discord.Colour.gold()
							)
							embed.set_author(
								name = ctx.author.name + "#" + ctx.author.discriminator,
								icon_url = ctx.author.avatar_url
							)

							await ctx.send(embed = embed)
							await ctx.channel.delete_messages(messagesList)
							roleChangeInProgress = False
							break

						else:
							embed = discord.Embed(
								title = "Custom Role Configuration",
								description = "❌ That's not a valid hex colour code.",
								colour = discord.Colour.gold()
							)
							embed.set_author(
								name = ctx.author.name + "#" + ctx.author.discriminator,
								icon_url = ctx.author.avatar_url
							)

							messagesList.append(await ctx.send(embed = embed))

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
					icon_url = ctx.author.avatar_url
				)
				embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

				messagesList.append(await ctx.send(embed = embed))

				try:
					response1 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
					messagesList.append(response1)
				except asyncio.TimeoutError:
					embed = discord.Embed(
						title = "Custom Role Configuration",
						description = "❌ Role configuration cancelled: timeout reached.",
						colour = discord.Colour.gold()
					)

					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.avatar_url
					)

					embed.set_footer(text = "This message will self-destruct in 5 minutes.")

					await ctx.send(embed = embed, delete_after = 300)
					await ctx.channel.delete_messages(messagesList)
					break

				if response1.content == "cancel":
					embed = discord.Embed(
						title = "Custom Role Configuration",
						description = "❌ Role configuration cancelled.",
						colour = discord.Colour.gold()
					)

					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.avatar_url
					)

					embed.set_footer(text = "This message will self-destruct in 5 minutes.")

					await ctx.send(embed = embed, delete_after = 300)
					await ctx.channel.delete_messages(messagesList)
					roleChangeInProgress = False
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
						icon_url = ctx.author.avatar_url
					)
					embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

					messagesList.append(await ctx.send(embed = embed))

					try:
						response2 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
						messagesList.append(response2)
					except asyncio.TimeoutError:
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role configuration cancelled: timeout reached.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.avatar_url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messagesList)
						break

					if response2.content == "cancel":
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role configuration cancelled.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.avatar_url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messagesList)
						roleChangeInProgress = False
						break

					else:
						userRoleId = server_data["custom_roles"][str(userId)]
						userRole = ctx.guild.get_role(userRoleId)

						if not userRole:
							await ctx.send("❌ Discord is being mean, please try again later.")
							roleChangeInProgress = False
							break

						await userRole.edit(
							name = response2.content
						)

						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = f"✅ Role name modified: {userRole.mention}",
							colour = discord.Colour.gold()
						)
						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.avatar_url
						)

						await ctx.send(embed = embed)
						await ctx.channel.delete_messages(messagesList)
						roleChangeInProgress = False
						break

				elif response1.content == "2":
					embed = discord.Embed(
						title = "Custom Role Configuration",
						colour = discord.Colour.gold()
					)
					embed.add_field(
						name = "2) Role Colour",
						value = "What do you want your role colour to be? Go to the link: https://htmlcolorcodes.com/ and find the HEX colour code (#00BD1A in the image below) for the colour you want. Paste the HEX code below and send it.",
						inline = False
					)
					embed.set_image(
						url = "https://i.imgur.com/seUpcRU.png"
					)
					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.avatar_url
					)
					embed.set_footer(text = "This process will be aborted if you don't reply within 5 minutes or you type `cancel`.")

					messagesList.append(await ctx.send(embed = embed))

					try:
						response2 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
						messagesList.append(response2)
					except asyncio.TimeoutError:
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role creation cancelled: timeout reached.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.avatar_url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messagesList)
						roleChangeInProgress = False
						break

					if response2.content == "cancel":
						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = "❌ Role creation cancelled.",
							colour = discord.Colour.gold()
						)

						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.avatar_url
						)

						embed.set_footer(text = "This message will self-destruct in 5 minutes.")

						await ctx.send(embed = embed, delete_after = 300)
						await ctx.channel.delete_messages(messagesList)
						roleChangeInProgress = False
						break

					else:
						def isHex(input):
							def removePrefix(input):
								if input.startswith("#"):
									return input[1:]
								else:
									return input
							
							formattedInput = removePrefix(input)
							
							if len(formattedInput) != 6:
								return False

							try:
								return int(removePrefix(input), 16)
							except ValueError:
								return False

						colourValue = isHex(response2.content)
						userRoleId = server_data["custom_roles"][str(userId)]
						userRole = ctx.guild.get_role(userRoleId)
						
						if not colourValue:
							embed = discord.Embed(
								title = "Custom Role Configuration",
								description = "❌ That's not a valid hex colour code.",
								colour = discord.Colour.gold()
							)
							embed.set_author(
								name = ctx.author.name + "#" + ctx.author.discriminator,
								icon_url = ctx.author.avatar_url
							)

							messagesList.append(await ctx.send(embed = embed))

						if not userRole:
							await ctx.send("❌ Discord is being mean, please try again later.")
							roleChangeInProgress = False
							break

						await userRole.edit(
							colour = colourValue
						)

						embed = discord.Embed(
							title = "Custom Role Configuration",
							description = f"✅ Role colour modified: {userRole.mention}",
							colour = discord.Colour.gold()
						)
						embed.set_author(
							name = ctx.author.name + "#" + ctx.author.discriminator,
							icon_url = ctx.author.avatar_url
						)

						await ctx.send(embed = embed)
						await ctx.channel.delete_messages(messagesList)
						roleChangeInProgress = False
						break

				else:
					embed = discord.Embed(
						title = "Custom Role Configuration",
						description = "❌ Invalid response; please try again.",
						colour = discord.Colour.gold()
					)
					embed.set_author(
						name = ctx.author.name + "#" + ctx.author.discriminator,
						icon_url = ctx.author.avatar_url
					)

					messagesList.append(await ctx.send(embed = embed))

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 5, commands.BucketType.user)
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
			value = roleStr,
			inline = False
		)

		await ctx.send(embed = embed)
		
	@commands.command(name = "rolePermissions", aliases = ["rperms"])
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def role_permissions(self, ctx, role: discord.Role):
		"""List the permissions of a given role."""

		perms = "\n".join(perm for perm, value in role.permissions if value)

		embed = discord.Embed(
			title = "Permissions for:",
			description = role.mention,
			colour = role.colour
		)

		embed.add_field(
			name = "\uFEFF",
			value = perms,
			inline = False
		)

		await ctx.send(embed = embed)

	@commands.command(name = "userPermissions", aliases = ["uperms"])
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def user_permissions(self, ctx, member: discord.Member = None):
		"""List the permissions of a given user."""

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
			value = perms,
			inline = False
		)

		await ctx.send(embed = embed)


def setup(client):
	client.add_cog(Roles(client))
