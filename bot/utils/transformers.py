import discord
from discord import app_commands
from discord.ext import commands

class MemberTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.Member:
		ctx = await interaction.client.get_context(interaction)
		return await commands.MemberConverter().convert(ctx, value)

class UserTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.User:
		ctx = await interaction.client.get_context(interaction)
		return await commands.UserConverter().convert(ctx, value)

class MessageTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.Message:
		ctx = await interaction.client.get_context(interaction)
		return await commands.MessageConverter().convert(ctx, value)

class TextChannelTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.TextChannel:
		ctx = await interaction.client.get_context(interaction)
		return await commands.TextChannelConverter().convert(ctx, value)

class VoiceChannelTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.VoiceChannel:
		ctx = await interaction.client.get_context(interaction)
		return await commands.VoiceChannelConverter().convert(ctx, value)

class StageChannelTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.StageChannel:
		ctx = await interaction.client.get_context(interaction)
		return await commands.StageChannelConverter().convert(ctx, value)

class CategoryChannelTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.CategoryChannel:
		ctx = await interaction.client.get_context(interaction)
		return await commands.CategoryChannelConverter().convert(ctx, value)

class ForumChannelTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.ForumChannel:
		ctx = await interaction.client.get_context(interaction)
		return await commands.ForumChannelConverter().convert(ctx, value)

class ThreadTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.Thread:
		ctx = await interaction.client.get_context(interaction)
		return await commands.ThreadConverter().convert(ctx, value)

class RoleTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.Role:
		ctx = await interaction.client.get_context(interaction)
		return await commands.RoleConverter().convert(ctx, value)

class ColourTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.Colour:
		ctx = await interaction.client.get_context(interaction)
		return await commands.ColourConverter().convert(ctx, value)

class EmojiTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.Emoji:
		ctx = await interaction.client.get_context(interaction)
		return await commands.EmojiConverter().convert(ctx, value)

class PartialEmojiTransformer(app_commands.Transformer):
	@classmethod
	async def transform(cls, interaction: discord.Interaction, value: str | int) -> discord.PartialEmoji:
		ctx = await interaction.client.get_context(interaction)
		return await commands.PartialEmojiConverter().convert(ctx, value)
