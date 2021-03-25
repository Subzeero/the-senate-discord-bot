import discord, traceback
from discord.ext import commands
from replit import db

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

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.channel.id == suggestionsChannelId and db["suggestionReactionsEnabled"]:
			await message.add_reaction("👍")
			await message.add_reaction("👎")

def setup(client):
	client.add_cog(Events(client))
	