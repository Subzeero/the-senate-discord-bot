import discord, asyncio
from discord.ext import commands
import database as db

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
	@commands.cooldown(1, 7, commands.BucketType.user)
	async def changeRole(self, ctx):
		"""[WIP]"""

		serverId = str(ctx.guild.id)
		userId = ctx.author.id
		server_data = db.validate_server(serverId)

		def validateMessage(message):
			return message.author == ctx.author

		if not userId in server_data["custom_roles"]:
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

			message1 = await ctx.send(embed = embed)

			try:
				response1 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
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

				await ctx.send(embed = embed)
				await ctx.message.delete()
				await response1.delete()
				await message1.delete()
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

				await ctx.send(embed = embed)
				await ctx.message.delete()
				await response1.delete()
				await message1.delete()
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

					message2 = await ctx.send(embed = embed)

					try:
						response2 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
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

						await ctx.send(embed = embed)
						await ctx.message.delete()
						await message1.delete()
						await message2.delete()
						await response1.delete()
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

						await ctx.send(embed = embed)
						await ctx.message.delete()
						await message1.delete()
						await message2.delete()
						await response1.delete()
						await response2.delete()
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
							newRole = await ctx.guild.create_role(
								name = response1.content,
								colour = colourValue,
								reason = "Created by user command."
							)

							await ctx.author.add_roles(newRole)

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
							# save role data
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

							await ctx.send(embed = embed)

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

				message1 = await ctx.send(embed = embed)

				try:
					response1 = await self.client.wait_for("message", check = validateMessage, timeout = 300)
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

					await ctx.send(embed = embed)
					await ctx.message.delete()
					await response1.delete()
					await message1.delete()
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

					await ctx.send(embed = embed)
					await ctx.message.delete()
					await response1.delete()
					await message1.delete()
					return

				elif response1.content == "1" or response1.contect == "2":
					embed = discord.Embed(
						title = "Custom Role Configuration"
					)

				else:
					embed = discord.Embed(
						title = "Invalid"
					)

		#db["server_data"] = server_data
		#serverRoles = await ctx.guild.fetch_roles()

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
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
		
	@commands.command(name = "rolepermissions", aliases = ["roleperms"])
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

	@commands.command(aliases = ["listperms", "perms"])
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	async def permissions(self, ctx, member: discord.Member = None):
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
