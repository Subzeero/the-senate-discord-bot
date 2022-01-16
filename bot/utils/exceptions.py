from discord.ext import commands

class MissingPermissions(commands.CheckFailure):
	pass

class UserOnGlobalCooldown(commands.CheckFailure):
	pass

class UnicodeEmojiNotFound(commands.BadArgument):
	def __init__(self, argument):
		self.argument = argument
		super().__init__(f"Unicode emoji '{argument}' not found.")
