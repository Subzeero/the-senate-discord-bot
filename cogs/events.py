import discord, replit
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
		await self.client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "over you :D"))

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.errors.CheckFailure):
			await ctx.send("❌ You don't have permission to run this command!")

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.channel.id == suggestionsChannelId and db["suggestionReactionsEnabled"]:
			await message.add_reaction("👍")
			await message.add_reaction("👎")
		#await self.client.process_commands(message)

def setup(client):
	client.add_cog(Events(client))
	