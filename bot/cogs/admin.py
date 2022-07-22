import discord
from discord import app_commands
from discord.ext import commands
from database.db import Database as db
from utils import transformers

class admin(commands.Cog, name = "Admin"):
	"""Administrator commands."""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.guilds(discord.Object(id=831000735671123988)) ## REMOVE ME
	@app_commands.default_permissions(administrator=True)
	@app_commands.describe(new_prefix="The new prefix to use (leave blank for default).")
	@app_commands.rename(new_prefix="prefix")
	async def changeprefix(self, interaction: discord.Interaction, new_prefix: str = None) -> None:
		"""Change the bot's prefix for text commands."""

		await interaction.response.defer(thinking=True, ephemeral=True)

		guild_data = db.get_guild(interaction.guild.id)
		guild_data["custom_prefix"] = new_prefix
		db.set_guild(interaction.guild.id, guild_data)

		embed = discord.Embed(description=f"✅ {'Prefix Changed!' if new_prefix else 'Prefix Reset to Default'}", colour=discord.Colour.green())
		await interaction.followup.send(embed=embed, ephemeral=True)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.guilds(discord.Object(id=831000735671123988)) ## REMOVE ME
	@app_commands.default_permissions(administrator=True)
	@app_commands.describe(message_type="The type of message to send.", content="The content to send.", channel="The TextChannel to send to.")
	@app_commands.choices(
		message_type=[
			app_commands.Choice(name="message", value=0),
			app_commands.Choice(name="embed", value=1)
		]
	)
	async def send(self, interaction: discord.Interaction, message_type: app_commands.Choice[int], content: str, channel: app_commands.Transform[discord.TextChannel, transformers.TextChannelTransformer] = None) -> None:
		"""Send a message or embed from the bot."""

		await interaction.response.defer(thinking=True, ephemeral=True)

		channel = channel if channel else interaction.channel
		if message_type.value:
			await channel.send(embed=discord.Embed(description=content, colour=discord.Colour.gold()))
		else:
			await channel.send(content)

		embed = discord.Embed(description=f"✅ {'Message' if message_type else 'Embed'} sent to {channel.mention}", colour=discord.Colour.green())
		await interaction.followup.send(embed=embed, ephemeral=True)

	@send.autocomplete("channel")
	async def send_autocomplete(self, interaction: discord.Interaction, current_channel: str) -> list[app_commands.Choice[str]]:
		channels = interaction.guild.text_channels
		return [app_commands.Choice(name=channel.name, value=channel.name) for channel in channels if current_channel in channel.name][:25]

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.guilds(discord.Object(id=831000735671123988)) ## REMOVE ME
	@app_commands.default_permissions(administrator=True)
	@app_commands.describe(message="The message to edit (CHNL_ID-MSG_ID, MSG_ID, or link).", message_type="The type of message to send.", content="The content to send.")
	@app_commands.choices(
		message_type=[
			app_commands.Choice(name="message", value=0),
			app_commands.Choice(name="embed", value=1)
		]
	)
	async def edit(self, interaction: discord.Interaction, message: app_commands.Transform[discord.Message, transformers.MessageTransformer], message_type: app_commands.Choice[int], content: str) -> None:
		"""Edit a message or embed from the bot."""

		await interaction.response.defer(thinking=True, ephemeral=True)

		if message_type.value:
			await message.edit(content=None, embed=discord.Embed(description=content, colour=discord.Colour.gold()))
		else:
			await message.edit(content=content, embed=None)

		embed = discord.Embed(description=f"✅ {'Message' if message_type else 'Embed'} `{message.id}` has been edited.", colour=discord.Colour.green())
		await interaction.followup.send(embed=embed, ephemeral=True)

	@app_commands.command()
	@app_commands.guild_only()
	@app_commands.guilds(discord.Object(id=831000735671123988)) ## REMOVE ME
	@app_commands.default_permissions(administrator=True)
	@app_commands.describe(
		message="The message to react to.",
		reaction1="An emoji to react with.",
		reaction2="An emoji to react with.",
		reaction3="An emoji to react with.",
		reaction4="An emoji to react with.",
		reaction5="An emoji to react with."
	)
	async def react(
		self,
		interaction: discord.Interaction,
		message: app_commands.Transform[discord.Message, transformers.MessageTransformer],
		reaction1: app_commands.Transform[discord.PartialEmoji, transformers.PartialEmojiTransformer],
		reaction2: app_commands.Transform[discord.PartialEmoji, transformers.PartialEmojiTransformer] = None,
		reaction3: app_commands.Transform[discord.PartialEmoji, transformers.PartialEmojiTransformer] = None,
		reaction4: app_commands.Transform[discord.PartialEmoji, transformers.PartialEmojiTransformer] = None,
		reaction5: app_commands.Transform[discord.PartialEmoji, transformers.PartialEmojiTransformer] = None
	) -> None:
		"""Add reactions to a message."""

		await interaction.response.defer(thinking=True, ephemeral=True)

		reactions = []
		for reaction in [reaction1, reaction2, reaction3, reaction4, reaction5]:
			if reaction:
				await message.add_reaction(reaction)
				reactions.append(str(reaction))

		await interaction.followup.send(embed=discord.Embed(description=f"✅ Reacted with {', '.join(reactions)}.", colour=discord.Colour.green()), ephemeral=True)

async def setup(bot: commands.Bot):
	await bot.add_cog(admin(bot))
