import discord
from discord.ext import commands
from helpers import debug

suggestionsChannelId = 796553486677311510

class Suggestions(commands.Cog):
	"""Command for server suggestions"""

	def __init__(self, client):
		self.client = client

	def check_Channel(ctx):
		whitelistedChannels = debug.get_testing_channels()
		whitelistedChannels.append(suggestionsChannelId)

		return ctx.message.channel.id in whitelistedChannels

	@commands.command()
	@commands.check(check_Channel)
	async def suggest(self, ctx, *, suggestion: str):
		"""Make a suggestion; only works in #suggestions."""

		message = await ctx.channel.send("Working...")
		await ctx.message.delete()

		await message.add_reaction("👍")
		await message.add_reaction("👎")

		embed = discord.Embed(
			description = suggestion,
			colour = discord.Colour.gold()
		)
		embed.set_author(
			name = f"Suggestion by {str(ctx.author)}",
			icon_url = ctx.author.avatar_url
		)
		embed.set_footer(text = f"Vote by reacting to the emotes below! SuggestionID: {message.id}")

		await message.edit(content = None, embed = embed)

	@commands.command()
	@commands.check(check_Channel)
	async def deleteSuggestion(self, ctx, suggestionID: int):
		"""Request for a suggestion to be deleted."""

		owner = ctx.guild.get_member(296406728818425857)
		
		await ctx.message.delete()
		await owner.send(f"{ctx.author.mention} has requested for the suggestion with id `{suggestionID}` to be deleted.")

		embed = discord.Embed(
			description = f"✅ Suggestion deletion requested.",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

def setup(client):
	client.add_cog(Suggestions(client))
