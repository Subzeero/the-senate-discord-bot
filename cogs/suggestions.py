import discord
from discord.ext import commands

suggestionsChannelId = 796553486677311510

class Suggestions(commands.Cog):
	"""Command for server suggestions"""

	def __init__(self, client):
		self.client = client

	def check_Channel(ctx):
		return ctx.message.channel.id == suggestionsChannelId

	@commands.command()
	@commands.check(check_Channel)
	async def suggest(self, ctx, *, suggestion: str):
		"""Make a suggestion; only works in #suggestions."""

		suggestionsChannel = self.client.get_channel(suggestionsChannelId)

		message = await suggestionsChannel.send("Working...")
		await ctx.message.delete()

		await message.add_reaction("👍")
		await message.add_reaction("👎")

		embed = discord.Embed(
			colour = discord.Colour.gold()
		)
		embed.add_field(
			name = "\uFEFF",
			value = ctx.message.content,
			inline = False
		)
		embed.set_author(
			name = f"Suggestion by {ctx.author.mention}",
			icon_url = ctx.author.avatar_url
		)
		embed.set_footer(text = "Vote by reacting to the emotes below! ID: {message.id}")

		await message.edit(content = None, embed = embed)

	@commands.command()
	@commands.check(check_Channel)
	async def deleteSuggestion(self, ctx, suggestionID: int):
		"""Request for a suggestion to be deleted."""

		ownerId = self.client.owner_Id
		owner = self.client.get_user(ownerId)

		await owner.send(f"{ctx.author.mention} has requested for the suggestion with id: `{suggestionID}` to be deleted.")

		embed = discord.Embed(
			description = f"✅ Suggestion deletion requested.",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

def setup(client):
	client.add_cog(Suggestions(client))
