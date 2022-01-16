import time, traceback
from discord.ext import commands, tasks
from utils import cooldown, exceptions

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
		users_to_remove = []
		for user, data in self.users_on_cooldown.items():
			if data["time"] < time.time():
				users_to_remove.append(user)

		for user in users_to_remove:
			self.users_on_cooldown.pop(user)

	async def abide_cooldown(self, user, ctx, content = None, embed = None):
		if not str(user.id) in self.users_on_cooldown.keys():
			self.users_on_cooldown[str(user.id)] = {
				"quota": 0,
				"time": 0
			}

		if self.users_on_cooldown[str(user.id)]["quota"] < 3 and self.users_on_cooldown[str(user.id)]["time"] == 0:
			self.users_on_cooldown[str(user.id)]["quota"] += 1
			if self.users_on_cooldown[str(user.id)]["quota"] == 3:
				self.users_on_cooldown[str(user.id)]["time"] = time.time() + 20
				if not content:
					content = f"Easy on the spam {user.mention}! Consider yourself ignored for the next while 🙊."
				else:
					content += f"\n\nEasy on the spam {user.mention}! Consider yourself ignored for the next while 🙊."
			await ctx.send(content = content, embed = embed)

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
			await self.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.CommandOnCooldown):
			message = f"❌ Slow down {ctx.author.mention}, you're running commands too fast!"
			await self.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.MaxConcurrencyReached):
			message = f"❌ The maximum number of users (`{error.number}`) are already running this command. Please try again later."
			await self.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.CommandNotFound):
			prefix = ctx.prefix
			content = ctx.message.content
			message = f"❌ `{content.replace(prefix, '')}` is not a registered command."
			await self.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.NoPrivateMessage):
			try:
				message = f"❌ `{ctx.command}` cannot be used in Private Messages."
				await self.abide_cooldown(ctx.author, ctx, content = message)
			except:
				pass

		elif isinstance(error, commands.PrivateMessageOnly):
			try:
				message = f"❌ `{ctx.command}` can only be used in Private Messages."
				await self.abide_cooldown(ctx.author, ctx, content = message)
			except:
				pass

		elif isinstance(error, commands.UserInputError):
			message = f"❌ {error} Type `{ctx.prefix}help {ctx.command}` for more information."
			await self.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.NotOwner):
			pass # Ignore

		elif isinstance(error, commands.CheckFailure):
			print(ctx.command.checks)
			message = "❌ You don't have permission to run this command!"
			await self.abide_cooldown(ctx.author, ctx, content = message)

		elif isinstance(error, commands.ExtensionError):
			await ctx.send(f"❌ Extension Error: {error}")
			traceback.print_exception(type(error), error, error.__traceback__)

		else:
			await ctx.send(f"❌ An error has occurred: `{type(error)}: {error}`\nhttps://tenor.com/tFAk.gif")
			traceback.print_exception(type(error), error, error.__traceback__)

def setup(client):
	client.add_cog(error_handler(client))
