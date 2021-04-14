import discord
from discord.ext import commands
import database as db
# View DB:
# curl "https://databasemanager.ironblockhd.repl.co/g/" --get -d $REPLIT_DB_URL

activityReference = {
	"playing": discord.ActivityType.playing,
	"streaming": discord.ActivityType.streaming,
	"listening": discord.ActivityType.listening,
	"watching": discord.ActivityType.watching,
	"competing": discord.ActivityType.competing
}

statusReference = {
	"online": discord.Status.online,
	"idle": discord.status.idle,
	"dnd": discord.status.dnd,
	"invisible": discord.status.invisible
}

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
	async def changeStatusType(self, ctx, newStatusStr):
		"""Change the bot's status type.
		Valid status types: `online`, `idle`, `dnd`, `invisible`."""
		None

	@commands.command()
	@commands.is_owner()
	async def changeStatusMessage(self, ctx, *, newStatusMessage: str):
		"""Change the bot's status.
		Any text is valid."""

		await ctx.message.delete()

		status_data = db.get("bot_status")
		status_data["message"] = newStatusMessage
		db.set("bot_status", status_data)

		await self.client.change_presence(activity = discord.Activity(type = activityReference[status_data["activity"]], name = newStatus))

		embed = discord.Embed(
			description = "✅ Successfully changed the bot's status!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def changeStatusActivity(self, ctx, newActivityStr: str):
		"""Change the bot's activity.
		Valid activity types: `playing`, `streaming`, `listening`, `watching`, `competing`."""

		await ctx.message.delete()
		
		if newActivityStr.lower() in activityReference:
			newActivity = activityReference[newActivityStr]
		else:
			await ctx.send("❌ That is not a valid activity type!")
			return
		
		status_data = db.get("bot_status")
		status_data["activity"] = newActivityStr
		db.set("bot_status", status_data)

		await self.client.change_presence(activity = discord.Activity(type = newActivity, name = status_data["status"]))

		embed = discord.Embed(
			description = "✅ Successfully changed the bot's activity!",
			colour = discord.Colour.gold()
		)

		embed.set_author(name = ctx.author.name + "#" + ctx.author.discriminator, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = "This message will self-destruct in 10 seconds.")

		await ctx.send(embed = embed, delete_after = 10)

	@commands.command()
	@commands.is_owner()
	async def startMaintenance(self, ctx):
		"""Enter maintenance mode."""
		None

	@commands.command()
	@commands.is_owner()
	async def stopMaintenance(self, ctx):
		"""End maintenance mode."""
		None

	@commands.command(aliases = ["close", "stop"])
	@commands.is_owner()
	async def shutdown(self, ctx):
		"""Shutdown the bot."""

		await ctx.message.delete()
		await self.client.change_presence(status = discord.Status.invisible)
		await self.client.close()


def setup(client):
	client.add_cog(Admin(client))
