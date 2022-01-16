import traceback
from discord.ext import commands
from utils import cooldown, exceptions

class error_handler(commands.Cog, name = "Error Handler"):
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
			message = f"❌ {ctx.command} has been disabled!"
			await cooldown.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.CommandOnCooldown):
			message = f"❌ Slow down {ctx.author.mention}, you're running commands too fast!"
			await cooldown.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.MaxConcurrencyReached):
			message = f"❌ This command is already running a maximum of `{error.number}` times right now. Please try again later."
			await cooldown.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.CommandNotFound):
			prefix = ctx.prefix
			content = ctx.message.content
			message = f"❌ `{content.replace(prefix, '')}` is not a registered command."
			await cooldown.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				message = f"❌ `{ctx.command}` cannot be used in Private Messages."
				await cooldown.abide_cooldown(ctx.author, ctx, content = message)
			except:
				pass

		elif isinstance(error, commands.PrivateMessageOnly):
			try:
				message = f"❌ `{ctx.command}` can only be used in Private Messages."
				await cooldown.abide_cooldown(ctx.author, ctx, content = message)
			except:
				pass

		elif isinstance(error, commands.UserInputError):
			message = f"❌ {error} Type `{ctx.prefix}help {ctx.command}` for more information."
			await cooldown.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, exceptions.UserOnGlobalCooldown):
			pass

		elif isinstance(error, commands.CheckFailure):
			message = "❌ You don't have permission to run this command!"
			await cooldown.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.ExtensionError):
			await ctx.send(f"❌ Extension Error: {error}")
			traceback.print_exception(type(error), error, error.__traceback__)

		else:
			await ctx.send(f"❌ An error has occurred: `{type(error)}: {error}`\nhttps://tenor.com/tFAk.gif")
			traceback.print_exception(type(error), error, error.__traceback__)

def setup(client):
	client.add_cog(error_handler(client))
