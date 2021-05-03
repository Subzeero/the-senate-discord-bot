import discord
from discord.ext import commands

class Admin(commands.Cog):
	"""Server administrator commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["say"])
	@commands.is_owner()
	async def echo(self, ctx, *, content:str):
		"""Echo a message back from the bot."""

		await ctx.message.delete()
		await ctx.send(content)

	@commands.command(aliases = ["edit"])
	@commands.is_owner()
	async def editMessage(self, ctx, messageID:int, newContent:str):
		"""Edit a message from the bot."""

		await ctx.message.delete()

		try:
			message = ctx.fetch_message(messageID)
		except discord.NotFound:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		if message.author.id == self.user.id:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		await message.edit(content = newContent, embed = None)

	@commands.command(aliases = ["sayembed"])
	@commands.is_owner()
	async def echoEmbed(self, ctx, channel:discord.TextChannel, *, content:str):
		"""Make an announcement."""

		embed = discord.Embed(
			description = content,
			colour = discord.Colour.gold()
		)

		await ctx.message.delete()
		await channel.send(embed = embed)

	@commands.command()
	@commands.is_owner()
	async def editEmbedMessage(self, ctx, messageID:int, *, newContent:str):
		"""Edit a message with an embed."""

		await ctx.message.delete()

		try:
			message = ctx.fetch_message(messageID)
		except discord.NotFound:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		if message.author.id == self.user.id:
			await ctx.send(content = f"❌ Invalid messageID: `{messageID}`!", delete_after = 3)
			return

		embed = discord.Embed(
			description = newContent,
			colour = discord.Colour.gold()
		)

		await message.edit(content = None, embed = embed)

def setup(client):
	client.add_cog(Admin(client))
