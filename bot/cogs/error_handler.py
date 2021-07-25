import traceback
from discord.ext import commands

class ErrorHandler(commands.Cog):
	"""Global error handler"""

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if hasattr(ctx.command, "on_error"):
			return

		if ctx.cog:
			if ctx.cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
				return

		error = getattr(error, "original", error)

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(f"❌ {ctx.command} has been disabled!")

		if isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"❌ Slow down {ctx.author.mention}, you're running commands too fast!")

		if isinstance(error, commands.MaxConcurrencyReached):
			await ctx.send(f"❌ The maximum number of users (`{error.number}`) are already running this command. Please try again later.")

		elif isinstance(error, commands.CommandNotFound):
			prefix = ctx.prefix
			content = ctx.message.content
			await ctx.send(f"❌ `{content.replace(prefix, '')}` is not a registered command.")

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(f"❌ `{ctx.command}` cannot be used in Private Messages.")
			except:
				pass

		elif isinstance(error, commands.PrivateMessageOnly):
			try:
				await ctx.send(f"❌ `{ctx.command}` can only be used in Private Messages.")
			except:
				pass

		elif isinstance(error, commands.UserInputError):
			await ctx.send(f"❌ {error}. Type `;help {ctx.command}` to see the proper arguments.")

		# elif isinstance(error, commands.BadArgument):
		# 	await ctx.send(f"❌ An API error occurred or the requested content could not be found. Please try again later.")

		elif isinstance(error, commands.CheckFailure):
			await ctx.send("❌ You don't have permission to run this command!")

		elif isinstance(error, commands.ExtensionError):
			await ctx.send(f"❌ Extension Error: {error}")

		else:
			await ctx.send(f"❌ An error has occurred: `{type(error)}: {error}`\nhttps://tenor.com/tFAk.gif")
			traceback.print_exception(type(error), error, error.__traceback__)

def setup(client):
	client.add_cog(ErrorHandler(client))
