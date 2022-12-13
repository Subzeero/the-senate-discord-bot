import discord, os, sys
from discord import app_commands
from discord.ext import commands
from database.db import Database as db
from pprint import pformat
from utils import bot_status, cooldown, checks

def restart_program() -> None:
	python = sys.executable
	os.execl(python, python, * sys.argv)

class fileEditorView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.new_file_content = None
		self.appending = True
		self.cancelled = False

	@discord.ui.button(label="Append", style=discord.ButtonStyle.primary)
	async def append_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		if await checks.is_owner_slash(interaction):
			modal = fileEditorModal()
			await interaction.response.send_modal(modal)
			await modal.wait()
			self.appending = True
			self.new_file_content = modal.new_file_content
			self.stop()
			self.append_button.disabled = True
			self.overwrite_button.disabled = True
			self.cancel_button.disabled = True
			await self.original_msg.edit(view=self)
		else:
			await interaction.response.send_message(embed=(discord.Embed(description="❌ This isn't yours!", colour=discord.Colour.red()).set_image(url="https://media.tenor.com/1YQDHEd7njoAAAAC/nope-no.gif")), ephemeral=True)

	@discord.ui.button(label="Overwrite", style=discord.ButtonStyle.danger)
	async def overwrite_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		if await checks.is_owner_slash(interaction):
			modal = fileEditorModal()
			await interaction.response.send_modal(modal)
			await modal.wait()
			self.appending = False
			self.new_file_content = modal.new_file_content
			self.stop()
			self.append_button.disabled = True
			self.overwrite_button.disabled = True
			self.cancel_button.disabled = True
			await self.original_msg.edit(view=self)
		else:
			await interaction.response.send_message(embed=(discord.Embed(description="❌ This isn't yours!", colour=discord.Colour.red()).set_image(url="https://media.tenor.com/1YQDHEd7njoAAAAC/nope-no.gif")), ephemeral=True)

	@discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
	async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
		if await checks.is_owner_slash(interaction):
			self.cancelled = True
			self.stop()
			self.append_button.disabled = True
			self.overwrite_button.disabled = True
			self.cancel_button.disabled = True
			await interaction.response.edit_message(view=self)
		else:
			await interaction.response.send_message(embed=(discord.Embed(description="❌ This isn't yours!", colour=discord.Colour.red()).set_image(url="https://media.tenor.com/1YQDHEd7njoAAAAC/nope-no.gif")), ephemeral=True)

class fileEditorModal(discord.ui.Modal, title="File Editor"):
	editor = discord.ui.TextInput(
		label="File Content:",
		style=discord.TextStyle.long,
		placeholder="Enter the file's contents...",
		required=True
	)

	async def on_submit(self, interaction: discord.Interaction) -> None:
		self.new_file_content = self.editor.value
		self.stop()
		await interaction.response.edit_message(view=self)

class owner(commands.Cog, name = "Owner"):
	"""Owner commands."""

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.ext_dirs = ["cogs", "bot/cogs"]
		self.loaded_cogs = []
		self.unloaded_cogs = []
		self.all_cogs = []

	@commands.Cog.listener()
	async def on_ready(self):
		print("Bot Running.")
		if not cooldown.manage_cooldowns.is_running():
			cooldown.manage_cooldowns.start()
			await bot_status.update_status(self.bot)

		self.loaded_cogs = []
		self.unloaded_cogs = []
		self.all_cogs = []

		for dir in self.ext_dirs:
			if os.path.exists(dir):
				ext_path = dir
				break
		else:
			print("WARNING: cogs.owner.on_ready(): A cogs folder could not be located.")
			return

		for cog in self.bot.cogs.values():
			self.loaded_cogs.append(cog.__class__.__name__)

		for file_name in os.listdir(ext_path):
			if file_name.endswith(".py"):
				file_name = file_name[:-3]
				if not file_name in self.loaded_cogs:
					self.unloaded_cogs.append(file_name)
		self.all_cogs = self.loaded_cogs.copy()
		self.all_cogs.extend(self.unloaded_cogs)
		self.all_cogs.sort()
		self.loaded_cogs.sort()
		self.unloaded_cogs.sort()

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		await db.set_guild(await db.get_guild(guild.id))

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

		if message.content.strip() == self.bot.user.mention:
			response = f"Hey {message.author.mention}!\n"
			response += f"I am a general purpose Discord bot destined to rule over {message.guild.name}.\n\n"
			response += "You can see my commands by typing `/` (older text commands no longer work)."

			embed = discord.Embed(description = response, colour = discord.Colour.gold())
			embed.set_image(url="https://media.tenor.com/AF9piIF5myUAAAAC/star-wars-i-am-the-senate.gif")
			
			await message.reply(embed = embed)

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	@app_commands.describe(
		status_type="The new status type for the bot.",
		status_activity="The status activity for the bot.",
		status_message="The status message for the bot.",
		maintenance="Enable the maintenance status."
	)
	@app_commands.choices(
		status_type=[
			app_commands.Choice(name="online", value="online"),
			app_commands.Choice(name="idle", value="idle"),
			app_commands.Choice(name="do not disturb", value="dnd"),
			app_commands.Choice(name="invisible", value="invisible")
		],
		status_activity=[
			app_commands.Choice(name="playing", value="playing"),
			app_commands.Choice(name="listening", value="listening"),
			app_commands.Choice(name="watching", value="watching"),
			app_commands.Choice(name="streaming", value="streaming"),
			app_commands.Choice(name="competing", value="competing"),
			app_commands.Choice(name="none", value="none")
		],
		maintenance=[
			app_commands.Choice(name="True", value=1),
			app_commands.Choice(name="False", value=0)
		]
	)
	async def changestatus(
		self,
		interaction: discord.Interaction,
		status_type: app_commands.Choice[str] = None,
		status_activity: app_commands.Choice[str] = None, 
		status_message: str = None,
		maintenance: app_commands.Choice[int] = None,
	) -> None:
		"""Change the bot's status type."""

		await interaction.response.defer(thinking=True, ephemeral=True)

		changes = ""
		bot_data = await db.get_bot()

		if status_type is not None:
			status_reference = bot_status.get_reference_table("status")
			if status_type.value in status_reference:
				bot_data["status"] = status_type.value
				changes += f"Status Type set to `{status_type.name}`\n"
		
		if status_activity is not None:
			status_reference = bot_status.get_reference_table("activity")
			if status_activity.value in status_reference:
				bot_data["activity"] = status_activity.value
				changes += f"Status Activity set to `{status_activity.name}`"

		if status_message is not None:
			bot_data["message"] = status_message
			changes += f"Status Message set to `{status_message}`"

		if maintenance is not None:
			if maintenance.value:
				bot_data["maintenance"] = True
				changes += "Maintenance Status `Enabled`"
			else:
				bot_data["maintenance"] = False
				changes += "Maintenance Status `Disabled`"

		if changes:
			await db.set_bot(bot_data)
			await bot_status.update_status(self.bot)
		else:
			changes = "*No Changes Recorded*"
		
		embed = discord.Embed(description=f"✅ Bot Status Updated\n\n{changes}", colour=discord.Colour.green())
		await interaction.followup.send(embed=embed, ephemeral=True)

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	@app_commands.describe(cog="The cog to load.")
	async def load(self, interaction: discord.Integration, cog: str) -> None:
		"""Load a cog."""

		await self.bot.load_extension(f"cogs.{cog}")

		if not cog in self.loaded_cogs:
			self.loaded_cogs.append(cog)
			self.unloaded_cogs.remove(cog)

			bot_data = await db.get_bot()
			bot_data["loaded_cogs"] = self.loaded_cogs
			await db.set_bot(bot_data)

		await interaction.response.send_message(embed=discord.Embed(description=f"✅ `{cog}` has been loaded.", colour=discord.Color.green()), ephemeral=True)

	@load.autocomplete("cog")
	async def load_autocomplete(self, interaction: discord.Interaction, current_cog: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=cog, value=cog) for cog in self.unloaded_cogs if current_cog in cog][:25]

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	@app_commands.describe(cog="The cog to unload.")
	async def unload(self, interaction: discord.Integration, cog: str) -> None:
		"""Unload a cog."""

		await self.bot.unload_extension(f"cogs.{cog}")

		if cog in self.loaded_cogs:
			self.loaded_cogs.remove(cog)
			self.unloaded_cogs.append(cog)

			bot_data = await db.get_bot()
			bot_data["loaded_cogs"] = self.loaded_cogs
			await db.set_bot(bot_data)

		await interaction.response.send_message(embed=discord.Embed(description=f"✅ `{cog}` has been unloaded.", colour=discord.Color.green()), ephemeral=True)

	@unload.autocomplete("cog")
	async def unload_autocomplete(self, interaction: discord.Interaction, current_cog: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=cog, value=cog) for cog in self.loaded_cogs if current_cog in cog][:25]

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	@app_commands.describe(cog="The cog to reload.")
	async def reload(self, interaction: discord.Integration, cog: str) -> None:
		"""Unload a cog."""

		await self.bot.unload_extension(f"cogs.{cog}")
		await self.bot.load_extension(f"cogs.{cog}")

		await interaction.response.send_message(embed=discord.Embed(description=f"✅ `{cog}` has been reloaded.", colour=discord.Color.green()), ephemeral=True)
	
	@reload.autocomplete("cog")
	async def reload_autocomplete(self, interaction: discord.Interaction, current_cog: str) -> list[app_commands.Choice[str]]:
		return [app_commands.Choice(name=cog, value=cog) for cog in self.loaded_cogs if current_cog in cog][:25]

	@app_commands.command()
	@app_commands.guilds(discord.Object(id=831000735671123988))
	@app_commands.check(checks.is_owner_slash)
	async def listcogs(self, interaction: discord.Interaction) -> None:
		"""List extension/cog information."""
		
		self.loaded_cogs = []
		self.unloaded_cogs = []
		self.all_cogs = []

		for dir in self.ext_dirs:
			if os.path.exists(dir):
				ext_path = dir
				break
		else:
			await interaction.response.send_message(embed=discord.Embed(description="❌ A `cogs` folder could not be located.", colour=discord.Color.red()), ephemeral=True)
			return

		for cog in self.bot.cogs.values():
			self.loaded_cogs.append(cog.__class__.__name__)

		for file_name in os.listdir(ext_path):
			if file_name.endswith(".py"):
				file_name = file_name[:-3]
				if not file_name in self.loaded_cogs:
					self.unloaded_cogs.append(file_name)
		self.all_cogs = self.loaded_cogs.copy()
		self.all_cogs.extend(self.unloaded_cogs)
		self.all_cogs.sort()
		self.loaded_cogs.sort()
		self.unloaded_cogs.sort()

		embed = discord.Embed(
			title = 'Extension Information', 
			description = "The following cogs have been registered:", 
			colour = discord.Color.gold()
		)

		for cog in self.all_cogs:
			embed.add_field(
				name = cog, 
				value="✅ Loaded!" if cog in self.loaded_cogs else "⚠️ Not Loaded!",
				inline = True
			)
					
		await interaction.response.send_message(embed=embed)

	@commands.command()
	@commands.is_owner()
	async def syncGuild(self, ctx: commands.Context) -> None:
		"""Sync all slash commands to this guild."""
		synced = await ctx.bot.tree.sync(guild = ctx.guild)
		await ctx.reply(embed=discord.Embed(description=f"✅ Successfully synced `{len(synced)}` commands to this guild.", colour=discord.Color.green()))

	@commands.command()
	@commands.is_owner()
	async def syncGlobal(self, ctx: commands.Context) -> None:
		"""Sync all slash commands to all guilds."""
		synced = await ctx.bot.tree.sync()
		await ctx.reply(embed=discord.Embed(description=f"✅ Successfully synced `{len(synced)}` commands globally.", colour=discord.Color.green()))
	
	@commands.command()
	@commands.is_owner()
	async def getBotData(self, ctx: commands.Context) -> None:
		"""View the raw data saved for the bot."""
		bot_data = await db.get_bot()
		bot_data_str = pformat(bot_data, sort_dicts=False)
		while len(bot_data_str) > 0:
			await ctx.send("```py\n{}\n```".format(bot_data_str[:1975]))
			bot_data_str = bot_data_str[1975:]
	
	@commands.command()
	@commands.is_owner()
	async def getGuildData(self, ctx: commands.Context) -> None:
		"""View the raw data saved for this guild."""
		guild_data = await db.get_guild(ctx.guild.id)
		guild_data_str = pformat(guild_data, sort_dicts=False)
		while len(guild_data_str) > 0:
			await ctx.send("```py\n{}\n```".format(guild_data_str[:1975]))
			guild_data_str = guild_data_str[1975:]

	@commands.command()
	@commands.is_owner()
	async def getFiles(self, ctx: commands.Context, path: str = ".") -> None:
		"""View the bot files."""
		files = ""
		for file in os.listdir(path):
			if os.path.isdir(os.path.join(path, file)):
				files += file + os.path.sep + "\n"
			else:
				files += file + "\n"
		files = files[:-1]
		await ctx.send("```{}```".format(files))

	@commands.command()
	@commands.is_owner()
	async def viewFile(self, ctx: commands.Context, path: str) -> None:
		"""View the content of a file."""
		await ctx.send(file=discord.File(path))

	@commands.command()
	@commands.is_owner()
	async def editFile(self, ctx: commands.Context, path: str) -> None:
		"""Edit the content of a file."""
		try:
			if not os.path.isfile(path):
				raise FileNotFoundError

			view = fileEditorView()
			msg = await ctx.send(content=f"Edit `{path}`:", view=view)
			view.original_msg = msg
			await view.wait()

			if not view.cancelled:
				if view.appending:
					mode = "a"
				else:
					mode = "w"
				
				with open(path, mode) as file:
					file.write(view.new_file_content)
				await ctx.send(embed=discord.Embed(description=f"✅ File `{path}` updated.", colour=discord.Colour.green()))

		except:
			await ctx.send(embed=discord.Embed(description=f"❌ Invalid file `{path}`.", colour=discord.Colour.gold()))

	@commands.command()
	@commands.is_owner()
	async def shutdown(self, ctx: commands.Context) -> None:
		"""Shutdown the bot."""

		await ctx.message.delete()
		await self.bot.change_presence(status = discord.Status.invisible)
		await self.bot.close()

	@commands.command()
	@commands.is_owner()
	async def restart(self, ctx: commands.Context) -> None:
		"""Restart the bot."""

		await ctx.message.delete()
		await self.bot.change_presence(status = discord.Status.invisible)
		restart_program()

async def setup(bot: commands.Bot):
	await bot.add_cog(owner(bot))
