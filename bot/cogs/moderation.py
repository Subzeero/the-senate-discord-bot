import discord, math
from discord.ext import commands
from utils import checks, converters
from typing import Union

class moderation(commands.Cog, name = "Moderation"):
	"""Moderation commands."""

	def __init__(self, client):
		self.client = client
	
	@commands.command(aliases = ["delete"])
	@commands.guild_only()
	@commands.cooldown(1, 10, commands.BucketType.guild)
	@commands.max_concurrency(1, commands.BucketType.guild)
	@checks.is_admin_or_mod()
	async def purge(self, ctx, num_of_messages: int, user: discord.User = None):
		"""Purge a number of messages."""

		num_purged = 0
		def purgeCheck(message):
			nonlocal num_purged
			if message.id == ctx.message.id:
				return True

			if message == response:
				return False

			if num_purged >= num_of_messages:
				return False

			if user:
				if message.author.id == user.id:
					num_purged += 1
					return True
				else:
					return False

			else:		
				num_purged += 1
				return True

		if num_of_messages > 250:
			await ctx.send("❌ Please don't purge more than 250 messages at once.")
			return
		
		response = await ctx.send("Working...")

		while True:
			if num_purged < num_of_messages:
				await ctx.channel.purge(limit = math.floor(num_of_messages * 0.5 + 10), check = purgeCheck)
			else:
				break

		embed = discord.Embed(
			description = f"✅ Successfully purged `{num_of_messages}` messages.",
			colour = discord.Colour.green()
		)

		embed.set_author(
			name = f"{ctx.author.name}#{ctx.author.discriminator}",
			icon_url = ctx.author.avatar_url
		)

		embed.set_footer(text = "This message will self-destruct in 10 seconds.")
		
		await response.edit(content = None, embed = embed, delete_after = 10)

	@commands.command(name = "purgeBetween", aliases = ["deleteBetween"])
	@commands.guild_only()
	@commands.cooldown(1, 10, commands.BucketType.guild)
	@commands.max_concurrency(1, commands.BucketType.guild)
	@checks.is_admin_or_mod()
	async def purge_between(self, ctx, message1: discord.Message, message2: discord.Message):
		"""Purge everything in between two messages."""

		response = await ctx.send("Working...")

		if message1.id > message2.id:
			temp = message1
			message1 = message2
			message2 = temp

		message1_removed = False
		message2_removed = False
		num_purged = 0 
		
		def purgeCheck(message):
			nonlocal message1_removed, message2_removed, num_purged
			if message.id == ctx.message.id:
				return True

			if message == response:
				return False

			if message.id >= message1.id and message.id <= message2.id:
				if message.id == message1.id:
					message1_removed = True
				elif message.id == message2.id:
					message2_removed = True
				num_purged += 1
				return True

		while not message1_removed or not message2_removed:
			await ctx.channel.purge(limit = 15, check = purgeCheck)
			if num_purged > 250:
				await ctx.send(f"⚠️ Message Purging Cap Reached: `{num_purged}` messages")
				break

		embed = discord.Embed(
			description = f"✅ Successfully purged `{num_purged}` messages.",
			colour = discord.Colour.green()
		)

		embed.set_author(
			name = f"{ctx.author.name}#{ctx.author.discriminator}",
			icon_url = ctx.author.avatar_url
		)

		embed.set_footer(text = "This message will self-destruct in 10 seconds.")
		
		await response.edit(content = None, embed = embed, delete_after = 10)

	@commands.command()
	@commands.guild_only()
	@commands.cooldown(1, 3, commands.BucketType.user)
	@checks.is_admin_or_mod()
	async def react(self, ctx, message: discord.Message, *reactions: Union[discord.Emoji, converters.UnicodeEmojiConverter]):
		"""Add reactions to the specified message."""

		await ctx.message.delete()
		for reaction in reactions:
			await message.add_reaction(reaction)

def setup(client):
	client.add_cog(moderation(client))
