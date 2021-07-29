import discord, traceback
from discord.ext import commands
from database.db import Database as db

suggestionsChannelId = 796553486677311510

class Events(commands.Cog):
	"""Listen for the bot's events."""

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print("Bot Running.")

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		db.get_server(guild.id)

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

		if message.content == f"<@!{self.client.user.id}>":
			prefixes = await self.client.get_prefix(message)
			prefix_str = ""

			if isinstance(prefixes, list):
				for prefix in prefixes:
					if prefix.find(self.client.user.id) == -1:
						prefix_str = prefix_str + prefix
			elif isinstance(prefixes, str):
				prefix_str = prefixes

			embed = discord.Embed(
				description = f"My prefix in this server is `{prefix_str}`. You can also use my commands by pinging me before the command like: {self.client.user.mention}` help`",
				colour = discord.Colour.gold()
			)

			embed.set_author(name = str(message.author), icon_url = message.author.avatar_url)
			embed.set_footer(text = f"Use `{prefix_str}changePrefix` to change my prefix.")

			await message.channel.send(embed = embed)

		if message.channel.id == suggestionsChannelId and not message.content.startswith(";suggest "):
			embed = discord.Embed(
				description = "🛑 The only messages allowed in this channel are `;suggest <suggestion>` messages! Use #suggestion-discussion instead."
			)
			embed.set_author(
				name = str(message.author),
				icon_url = message.author.avatar_url
			)
			embed.set_footer(text = "This message will self-destruct in 10 seconds.")

			await message.delete()
			await message.channel.send(embed = embed, delete_after = 10)

		# print("author:", message.author.id, "message:", message.content)
		if message.author.id == 397879157029077002:
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

				embed = discord.Embed(
					description = f"You're not allowed to ping {invalidMention}! Now you can sit in silence until someone decides to unmute you. 🙊",
					colour = discord.Colour.gold()
				)
				embed.set_author(
					name = str(message.author),
					icon_url = message.author.avatar_url
				)

				await message.channel.send(embed = embed)

def setup(client):
	client.add_cog(Events(client))
