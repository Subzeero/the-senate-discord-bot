import discord, traceback
from discord import app_commands
from discord.ext import commands
from utils import cooldown, exceptions

class error_handler(commands.Cog, name = "Error Handler"):
	"""Global error handler."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		bot.tree.on_error = self.on_app_command_error

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if hasattr(ctx.command, "on_error"):
			return

		if ctx.cog:
			if ctx.cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
				return

		error = getattr(error, "original", error)

		if isinstance(error, exceptions.UserOnGlobalCooldown):
			pass
		else:
			embed = discord.Embed(description=f"❌ **{type(error).__name__}:** `{error}`", colour=discord.Colour.red())
			await cooldown.abide_cooldown(ctx.author, ctx, embed=embed)
			traceback.print_exception(type(error), error, error.__traceback__)

	async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
		error = getattr(error, "original", error)
		embed = discord.Embed(description=f"❌ **{type(error).__name__}:** `{error}`", colour=discord.Colour.red())
		if not interaction.response.is_done():
			await interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			await interaction.followup.send(embed=embed, ephemeral=True)
		traceback.print_exception(type(error), error, error.__traceback__)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(error_handler(bot))
