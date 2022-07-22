from discord.ext import commands
from utils import exceptions
import emojis, re

class UnicodeEmojiConverter(commands.Converter):
	async def convert(self, ctx, argument):
		if not (emoji := emojis.db.get_emoji_by_code(argument)):
			raise exceptions.UnicodeEmojiNotFound(argument)
		return emoji.emoji

time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"s":1, "m":60, "h":3600, "d":86400}
whitespace_regex = re.compile(r'\s+')

class RelativeTimeConverter(commands.Converter):
	async def convert(self, ctx, argument):
		time = 0
		try:
			num = int(argument)
		except:
			matches = time_regex.findall(whitespace_regex.sub("", argument.lower()))
			for num, determiner in matches:
				try:
					time += time_dict[determiner] * int(num)
				except KeyError:
					raise commands.BadArgument(f"`{determiner}` is invalid! Use `s`, `m`, `h`, or `d`.")
				except ValueError:
					raise commands.BadArgument(f"`{num}` in not a number!")
		else:
			time = num

		if time <= 0:
			raise commands.BadArgument(f"`{argument}` is not a valid time. Use `<num> <s | m | h | d>`.")
		return time
