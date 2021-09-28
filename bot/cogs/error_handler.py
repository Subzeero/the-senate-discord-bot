import time, traceback
from discord.ext import commands, tasks
from helpers import checks

class error_handler(commands.Cog, name = "Error Handler"):
	"""Global error handler"""

	def __init__(self, client):
		self.client = client

		self.users_on_cooldown = {}
		self.manage_cooldowns.start()

	def cog_unload(self):
		self.manage_cooldowns.cancel()

	@tasks.loop(seconds=30)
	async def manage_cooldowns(self):
		for user, secs in self.users_on_cooldown.items():
			if secs < time.time():
				self.users_on_cooldown.pop(user)

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

		elif isinstance(error, commands.CommandOnCooldown):
			if not str(ctx.author.id) in self.users_on_cooldown.keys():
				await ctx.send(f"❌ Slow down {ctx.author.mention}, you're running commands too fast!")
				self.users_on_cooldown[str(ctx.author.id)] = time.time() + 15

		elif isinstance(error, commands.MaxConcurrencyReached):
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
			await ctx.send(f"❌ {error} Type `{ctx.prefix}help {ctx.command}` for more information.")

		elif isinstance(error, commands.NotOwner):
			return

		elif isinstance(error, commands.CheckFailure):
			await ctx.send("❌ You don't have permission to run this command!")

		elif isinstance(error, commands.ExtensionError):
			await ctx.send(f"❌ Extension Error: {error}")
			traceback.print_exception(type(error), error, error.__traceback__)

		else:
			await ctx.send(f"❌ An error has occurred: `{type(error)}: {error}`\nhttps://tenor.com/tFAk.gif")
			traceback.print_exception(type(error), error, error.__traceback__)

def setup(client):
	client.add_cog(error_handler(client))
