import discord
from discord.ext import commands
from database.db import Database as db
from utils import cooldown

class events(commands.Cog, name = "Events"):
	"""Global event handler. Being phased out."""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print("Bot Running.")
		if not cooldown.manage_cooldowns.is_running():
			cooldown.manage_cooldowns.start()

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		db.set_guild(db.get_guild(guild.id))

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

		if message.content == f"<@!{self.bot.user.id}>":
			prefixes = await self.bot.get_prefix(message)
			prefix_str = ""

			if isinstance(prefixes, list):
				for prefix in prefixes:
					if not str(self.bot.user.id) in prefix:
						prefix_str = prefix
			elif isinstance(prefixes, str):
				prefix_str = prefixes

			embed = discord.Embed(
				description = f"My prefix in this server is: `{prefix_str}`\nUsage: `{prefix_str}help` or `@{self.bot.user.display_name} help`.",
				colour = discord.Colour.gold()
			)

			await message.reply(embed = embed)

		# if message.channel.id == suggestionsChannelId and not message.content.startswith(";suggest "):
		# 	embed = discord.Embed(
		# 		description = "🛑 The only messages allowed in this channel are `;suggest <suggestion>` messages! Use #suggestion-discussion instead."
		# 	)
		# 	embed.set_author(
		# 		name = str(message.author),
		# 		icon_url = message.author.display_avatar.url
		# 	)
		# 	embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		# 	await message.delete()
		# 	await message.channel.send(embed = embed, delete_after = 10)

		# TEMPORARILY DISABLE THIS. WORKING ON BETTER SOLUTION THAT ISN'T HARDCODED

		# print("author:", message.author.id, "message:", message.content)
		# if message.author.id == 397879157029077002:
		# 	invalidMention = None
			
		# 	if "<@!296406728818425857>" in message.content:
		# 		invalidMention = "<@!296406728818425857>"
		# 	else:
		# 		return

		# 	if message.guild:
		# 		muterole = message.guild.get_role(755925817028247644)
		# 		await message.author.add_roles(muterole)

		# 		embed = discord.Embed(
		# 			description = f"You're not allowed to ping {invalidMention}! Now you can sit in silence until someone decides to unmute you. 🙊",
		# 			colour = discord.Colour.gold()
		# 		)
		# 		embed.set_author(
		# 			name = str(message.author),
		# 			icon_url = message.author.avatar_url
		# 		)

		# 		await message.channel.send(embed = embed)

async def setup(bot: commands.Bot):
	await bot.add_cog(events(bot))
