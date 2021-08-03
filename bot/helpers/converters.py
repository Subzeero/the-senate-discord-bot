from discord.ext import commands
import emojis

class UnicodeEmojiNotFound(commands.BadArgument):
	def __init__(self, argument):
		self.argument = argument
		super().__init__(f"Unicode emoji '{argument}' not found.")

class UnicodeEmojiConverter(commands.Converter):
	async def convert(self, ctx, argument):
		if not (emoji := emojis.db.get_emoji_by_code(argument)):
			raise UnicodeEmojiNotFound(argument)
		return emoji.emoji
