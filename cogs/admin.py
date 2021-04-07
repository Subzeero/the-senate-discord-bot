import discord
from discord.ext import commands
import database as db
#View DB:
#curl "https://databasemanager.ironblockhd.repl.co/g/" --get -d $REPLIT_DB_URL

class Admin(commands.Cog):
	"""Administrator commands."""

	def __init__(self, client):
		self.client = client

	@commands.command(aliases = ["ssr", "sr"])
	@commands.is_owner()
	async def suggestionReactions(self, ctx, toggle:bool = True):
		"""Toggle auto-reactions for #server-suggestions."""

		await ctx.message.delete()

		db.set("suggestionReactionsEnabled", toggle)
		option = "enabled" if toggle else "disabled"

		embed = discord.Embed(
			#title = "Success!",
			description = f"✅ Auto reactions are now {option}!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command(aliases = ["say"])
	@commands.is_owner()
	async def echo(self, ctx, *, content:str):
		"""Echo a message back from the bot."""

		await ctx.message.delete()
		await ctx.send(content)

	@commands.command()
	@commands.is_owner()
	async def changeStatus(self, ctx, *, newStatus: str):
		"""Change the bot's status."""

		await ctx.message.delete()
		await self.client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = newStatus))

		embed = discord.Embed(
			#title = "Success!",
			description = "✅ Successfully changed the bot's status!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def changeActivity(self, ctx, *, newStatus: str):
		"""Change the bot's activity."""

		await ctx.message.delete()
		await self.client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = newStatus))

		embed = discord.Embed(
			#title = "Success!",
			description = "✅ Successfully changed the bot's status!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def shutdown(self, ctx):
		"""Shutdown the bot."""

		await ctx.message.delete()
		await self.client.change_presence(status = discord.Status.invisible)
		await self.client.close()


def setup(client):
	client.add_cog(Admin(client))
