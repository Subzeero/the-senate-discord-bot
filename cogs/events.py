import discord, traceback
from discord.ext import commands
import database as db

suggestionsChannelId = 796553486677311510

class Events(commands.Cog):
	"""Listen for the bot's events."""

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print("Bot Running.")
		await self.client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "over you :)"))

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		serverId = str(guild.id)
		db.validate_server(serverId)

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if hasattr(ctx.command, "on_error"):
			return

		if ctx.cog:
			if ctx.cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
				return

		#ignored = [] # No items wanted to be ignored
		error = getattr(error, "original", error)

		#if isinstance(error, ignored):
		#	return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(f"❌ {ctx.command} has been disabled!")

		if isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"❌ {ctx.author.mention}, you're running commands too fast.")

		elif isinstance(error, commands.CommandNotFound):
			await ctx.send(f"❌ `{ctx.message.content[1:]}` is not a registered command.")

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(f"❌ `{ctx.command}` cannot be used in Private Messages.")
			except discord.HTTPException:
				pass

		elif isinstance(error, commands.PrivateMessageOnly):
			try:
				await ctx.author.send(f"❌ `{ctx.command}` can only be used in Private Messages.")
			except discord.HTTPException:
				pass

		elif isinstance(error, commands.UserInputError):
			await ctx.send(f"❌ Invalid Arguments. Type `;help {ctx.command}` to see the proper arguments.")

		elif isinstance(error, commands.CheckFailure):
			await ctx.send("❌ You don't have permission to run this command!")

		elif isinstance(error, commands.ExtensionError):
			await ctx.send(f"❌ Extension Error: {error}")

		else:
			await ctx.send(f"❌ An error has occurred: `{type(error)}: {error}`\nhttps://tenor.com/tFAk.gif")
			traceback.print_exception(type(error), error, error.__traceback__)

	# @commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		if payload.event_type != "REACTION_ADD" or payload.user_id == 773066373693046826 or not payload.guild_id:
			return

		serverId = str(payload.guild_id)
		messageId = payload.message_id
		server = self.client.get_guild(int(serverId))
		emoji = payload.emoji
		user = server.get_member(payload.user_id)
		print(f"User: {user}")

		if not serverId or not user:
			return

		server_data = db.get_server(serverId)
		reactionRoleData = server_data["reaction_roles"]
		reactionRoleList = []

		for reactionName, reactionData in reactionRoleData.items():
			reactionRoleList.append({
				"messageId": reactionData["messageId"],
				"emojiId": reactionData["emojiId"],
				"roleId": reactionData["roleId"]
			})

		for data in reactionRoleList:
			if data["messageId"] == messageId and data["emojiId"] == emoji.id:
				role = server.get_role(data["roleId"])
				await user.add_roles(role)
				break

	# @commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		if payload.event_type != "REACTION_REMOVE" or payload.user_id == 773066373693046826 or not payload.guild_id:
			return

		serverId = str(payload.guild_id)
		messageId = payload.message_id
		server = self.client.get_guild(int(serverId))
		emoji = payload.emoji
		user = server.get_member(payload.user_id)
		print(f"User: {user}")

		if not serverId or not user:
			return

		server_data = db.get_server(serverId)
		reactionRoleData = server_data["reaction_roles"]
		reactionRoleList = []

		for reactionName, reactionData in reactionRoleData.items():
			reactionRoleList.append({
				"messageId": reactionData["messageId"],
				"emojiId": reactionData["emojiId"],
				"roleId": reactionData["roleId"]
			})

		for data in reactionRoleList:
			if data["messageId"] == messageId and data["emojiId"] == emoji.id:
				role = server.get_role(data["roleId"])
				await user.remove_roles(role)
				break

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.id == 773066373693046826 or message.author.id == 716390085896962058: # Ignore self and @Poketwo
			return

		if message.channel.id == suggestionsChannelId and db.get("suggestionReactionsEnabled"):
			await message.add_reaction("👍")
			await message.add_reaction("👎")

		# print("author:", message.author.id, "message:", message.content)
		if message.author.id == 397879157029077002:
			await message.delete()
			invalidMention = None
			
			if "<@!296406728818425857>" in message.content:
				invalidMention = "<@!296406728818425857>"
			elif "<@!355099018113843200>" in message.content:
				invalidMention = "<@!355099018113843200>"
			else:
				return

			if message.guild:
				muterole = message.guild.get_role(755925817028247644)
				await message.author.add_roles(muterole)
				await message.channel.send(f"You're not allowed to ping {invalidMention}! Now you can sit in silence until someone decides to unmute you.")

def setup(client):
	client.add_cog(Events(client))
