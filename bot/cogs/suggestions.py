import discord
from discord.ext import commands
from utils import debug

class suggestions(commands.Cog, name = "Suggestions"):
	"""Command for server suggestions"""

	def __init__(self, client):
		self.client = client

	def debug_check(ctx):
		if not ctx.guild:
			return False

		debug_data = debug.get_debug_data()
		return ctx.guild.id in debug_data["testing_guilds"] or ctx.channel.id in debug_data["suggestion_channels"]

	@commands.command()
	@commands.check(debug_check)
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
	@commands.check(debug_check)
	async def editSuggestion(self, ctx, suggestionID: int, *, newSuggestionText: str):
		"""Edit one of your suggestions."""

		progress = await ctx.send("Working...")
		await ctx.message.delete()

		try:
			message = await ctx.fetch_message(suggestionID)
		except discord.NotFound:
			await progress.edit(content = f"❌ Invalid suggestionID: `{suggestionID}`!", delete_after = 5)
			return

		debug_data = debug.get_debug_data()
		if message.channel.id in debug_data["suggestion_channels"] or message.guild.id in debug_data["testing_guilds"]:
			embedDict = message.embeds[0].to_dict()
			if not str(ctx.author) in embedDict["author"]["name"]:
				await progress.edit(content = "❌ You do not own this suggestion!", delete_after = 5)
				return
			
			embedDict["description"] = newSuggestionText
			await message.edit(embed = discord.Embed.from_dict(embedDict))
			await progress.edit(content = "✅ Suggestion successfully updated!", delete_after = 5)

		else:
			await progress.edit(content = f"❌ Invalid suggestionID: `{suggestionID}`!", delete_after = 5)			

	@commands.command()
	@commands.check(debug_check)
	async def deleteSuggestion(self, ctx, suggestionID: int):
		"""Request for a suggestion to be deleted."""

		owner = self.client.owner_id
		
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
	client.add_cog(suggestions(client))
