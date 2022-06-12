import asyncio, datetime, discord, inspect
from discord.ext import commands
from database.db import Database as db
from pprint import pformat
from utils import checks, find_object

class action_log(commands.Cog, name = "Action Log"):
	"""Manage the Action Log."""

	def __init__(self, client):
		self.client = client
		# all: (def: True, Priority 1) Enable log for all ids
		# inverse: (def: False, Priority 2) Enable log for only inputted ids. Otherwise all except inputted ids
		self.actions = {
			"message_deleted": {"channels": {"all": True, "inverse": False, "ids": []}, "members": {"all": True, "inverse": False, "ids": []}},
			"bulk_message_deleted": {"channels": {"all": True, "inverse": False, "ids": []}},
			"message_edited": {"channels": {"all": True, "inverse": False, "ids": []}, "members": {"all": True, "inverse": False, "ids": []}},
			"reaction_added": {"channels": {"all": True, "inverse": False, "ids": []}, "members": {"all": True, "inverse": False, "ids": []}},
			"reaction_removed": {"channels": {"all": True, "inverse": False, "ids": []}, "members": {"all": True, "inverse": False, "ids": []}},
			"reactions_cleared": {"channels": {"all": True, "inverse": False, "ids": []}},
			"channel_created": {},
			"channel_deleted": {"channels": {"all": True, "inverse": False, "ids": []}},
			"channel_updated": {"channels": {"all": True, "inverse": False, "ids": []}},
			"member_joined": {},
			"member_left": {},
			"member_banned": {},
			"member_unbanned": {},
			"member_updated": {"members": {"all": True, "inverse": False, "ids": []}},
			"role_created": {},
			"role_deleted": {},
			"role_updated": {"roles": {"all": True, "inverse": False, "ids": []}},
			"voice_activity_changed": {"members": {"all": True, "inverse": False, "ids": []}},
			"invite_created": {},
			"invite_deleted": {}
		}
		self.guild_action_data = {}

		self.log_cache = {}
		self.queued_guilds = []

		self.queuing_time = 20
		self.jump_link = "https://discord.com/channels/{guild}/{channel}/{message}"

		self.activity_types = {
			discord.ActivityType.playing: "playing",
			discord.ActivityType.streaming: "streaming",
			discord.ActivityType.listening: "listening",
			discord.ActivityType.watching: "watching",
			discord.ActivityType.competing: "competing",
			discord.activity.Game: "playing",
			discord.activity.Streaming: "streaming"
		}

	async def rule_check(self, rule, guild_id = None):
		if not guild_id:
			return False
		if not guild_id in self.guild_action_data:
			guild_data = db.get_guild(guild_id)
			self.guild_action_data[guild_id] = guild_data["action_log"]

		guild_rules = self.guild_action_data[guild_id]
		if guild_rules["enabled"] and rule in guild_rules["actions"]:
			rule_data = guild_rules["actions"][rule]
			if len(rule_data) == 0:
				return True
			return rule_data
		return False

	async def check_data(self, id, metadata):
		if self.client.user.id == id:
			return False
		elif metadata["all"]:
			return True
		elif metadata["inverse"]:
			return id in metadata["ids"]
		else:
			return not id in metadata["ids"]

	async def send_log(self, guild, embed):
		channel = await find_object.find_channel(self.client, self.guild_action_data[guild.id]["channel_id"])
		if channel:
			await channel.send(embed = embed)
		else:
			guild_data = db.get_guild(guild.id)
			guild_data["action_log"]["enabled"] = False
			guild_data["action_log"]["channel_id"] = 0
			self.guild_action_data[guild.id] = guild_data["action_log"]
			db.set_guild(guild.id, guild_data)

	async def enqueue_log(self, guild_id, log_data):
		if not guild_id in self.log_cache:
			self.log_cache[guild_id] = []
		self.log_cache[guild_id].append(log_data)

		if not guild_id in self.queued_guilds:
			self.queued_guilds.append(guild_id)
			while guild_id in self.queued_guilds:
				await asyncio.sleep(self.queuing_time)

				for guild_id, guild_logs in self.log_cache.items():
					guild = await find_object.find_guild(self.client, guild_id)
					embed = discord.Embed(colour = discord.Colour.gold())
					embed.set_author(name = "Actions Logged!", icon_url = guild.icon_url)

					num_logs = min(len(guild_logs), 10)
					for i in range(num_logs):
						embed.add_field(name = guild_logs[i][0], value = guild_logs[i][1], inline = False)
					embed.timestamp = datetime.datetime.utcnow()

					self.log_cache[guild_id] = guild_logs[num_logs:]
					if not len(self.log_cache[guild_id]):
						self.queued_guilds.remove(guild_id)

					await self.send_log(guild, embed)

	@commands.command(aliases = ["updateActionLog", "updateActionLogRules","refreshActionLogRules", "reloadActionLog", "reloadActionLogRules"])
	@commands.cooldown(1, 15, commands.BucketType.guild)
	@commands.guild_only()
	async def refreshActionLog(self, ctx):
		"""Refresh the Action Log Rules for your server."""

		guild_data = db.get_guild(ctx.guild.id)
		action_data = guild_data["action_log"]
		self.guild_action_data[ctx.guild.id] = action_data
		await ctx.message.add_reaction("✅")

	@commands.command(aliases = ["actionLogRules", "actionLog"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.guild_only()
	@checks.is_admin()
	async def listActionLogRules(self, ctx):
		"""List the action log rules in effect."""

		temp = await self.rule_check("Get Data", ctx.guild.id)
		guild_rules = self.guild_action_data[ctx.guild.id]

		if guild_rules["enabled"]:
			desc = f"Action Log: `✅ Enabled`"
		else:
			desc = f"Action Log: `❌ Disabled`"

		if guild_rules['channel_id']:
			desc = desc + f"\nLog Channel: <#{guild_rules['channel_id']}>"
		else:
			desc = desc + "\nLog Channel: `⚠️ None`"

		embed = discord.Embed(description = desc, colour = discord.Colour.gold())

		embed.set_author(name = f"Action Log Rules in {ctx.guild.name}", icon_url = ctx.guild.icon_url)
		embed.set_footer(text = f"If you don't see your rules, run {ctx.prefix}refreshActionLog.")
		
		if not guild_rules["actions"]:
			embed.add_field(name = "None!", value = f"Use `{ctx.prefix}addActionLogRule` to add some.")
		else:
			for r_name, r_rule in guild_rules["actions"].items():
				if isinstance(r_rule, bool):
					embed.add_field(name = r_name, value = f"`{r_rule}`".lower(), inline = False)
				else:
					embed.add_field(name = r_name, value = f"`{pformat(r_rule, sort_dicts = False, width=45)}`", inline = False)

		await ctx.send(embed = embed)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	@commands.guild_only()
	@checks.is_admin()
	async def setActionLogChannel(self, ctx, channel: discord.TextChannel = None):
		"""Set a channel for Action Log events."""

		guild_data = db.get_guild(ctx.guild.id)
		if channel:
			if channel.guild.id != ctx.guild.id:
				return await ctx.message.add_reaction("❌")
			else:
				guild_data["action_log"]["channel_id"] = channel.id
		else:
			guild_data["action_log"]["channel_id"] = 0
		db.set_guild(ctx.guild.id, guild_data)
		await ctx.message.add_reaction("✅")

	@commands.command(aliases = ["startActionLog"])
	@commands.cooldown(1, 5, commands.BucketType.guild)
	@commands.guild_only()
	@checks.is_admin()
	async def enableActionLog(self, ctx):
		"""Enable the Action Log."""

		guild_data = db.get_guild(ctx.guild.id)

		if guild_data["action_log"]["channel_id"]:
			guild_data["action_log"]["enabled"] = True
			db.set_guild(ctx.guild.id, guild_data)
			await ctx.invoke(self.refreshActionLog)
		else:
			await ctx.send("❌ Add an Action Log channel first.")

	@commands.command(aliases = ["stopActionLog"])
	@commands.cooldown(1, 5, commands.BucketType.guild)
	@commands.guild_only()
	@checks.is_admin()
	async def disableActionLog(self, ctx):
		"""Disable the Action Log."""

		guild_data = db.get_guild(ctx.guild.id)
		guild_data["action_log"]["enabled"] = False
		db.set_guild(ctx.guild.id, guild_data)

		await ctx.invoke(self.refreshActionLog)

	@commands.command(aliases = ["actionLogOptions", "actionLogDefaults"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.guild_only()
	@checks.is_admin()
	async def actionLogRulelist(self, ctx):
		"""List all of the possible Action Log Rules"""

		embed = discord.Embed(
			description = """- These are the rule options for the Action Log.
			- Each rule is presented with its default filtering options (or None).
			- `all` determines whether filtering will be applied.
			When True, no filtering; when False, filter according to `ids` and `inverse`.
			- `inverse` determines whether `ids` is a whitelist (when True)
			or a blacklist (when False, default).""",
			colour = discord.Colour.gold()
		)
		embed.set_author(name = "Action Log Rulelist")

		for r_name, r_rule in self.actions.items():
				if isinstance(r_rule, bool):
					embed.add_field(name = r_name, value = f"`{r_rule}`".lower(), inline = False)
				else:
					embed.add_field(name = r_name, value = f"`{pformat(r_rule, sort_dicts = False, width=45)}`", inline = False)
		await ctx.send(embed = embed)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	@commands.guild_only()
	@checks.is_admin()
	async def addActionLogRule(self, ctx, rule):
		"""Add an action log rule."""

		if rule.lower() in self.actions:
			guild_data = db.get_guild(ctx.guild.id)
			guild_data["action_log"]["actions"][rule] = self.actions[rule]
			db.set_guild(ctx.guild.id, guild_data)
			await ctx.message.add_reaction("✅")
		else:
			await ctx.send(f"❌ `{rule}` is not a valid rule.")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	@commands.guild_only()
	@checks.is_admin()
	async def removeActionLogRule(self, ctx, rule):
		"""Remove an action log rule."""

		guild_data = db.get_guild(ctx.guild.id)
		if rule in guild_data["action_log"]["actions"]:
			guild_data["action_log"]["actions"].pop(rule)
			db.set_guild(ctx.guild.id, guild_data)
			await ctx.message.add_reaction("✅")
		else:
			await ctx.send(f"❌ `{rule}` is not an enabled rule.")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	@commands.guild_only()
	@checks.is_admin()
	async def addAllActionLogRules(self, ctx, safetyCheck: bool):
		"""[NOT REVERSIBLE] Add all of the usable action log rules.
		Existing filtering options will be retained"""

		if safetyCheck:
			guild_data = db.get_guild(ctx.guild.id)
			for rule_name, rule_data in self.actions.items():
				if not rule_name in guild_data["action_log"]["actions"]:
					guild_data["action_log"]["actions"][rule_name] = rule_data
			db.set_guild(ctx.guild.id, guild_data)
			await ctx.send("✅ All rules have been added.")
		else:
			await ctx.send("❌ Safety check not satisfied.")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	@commands.guild_only()
	@checks.is_admin()
	async def removeAllActionLogRules(self, ctx, safetyCheck: bool):
		"""[NOT REVERSIBLE] Remove all of the action log rules in use."""

		if safetyCheck:
			guild_data = db.get_guild(ctx.guild.id)
			guild_data["action_log"]["actions"].clear()
			db.set_guild(ctx.guild.id, guild_data)
			await ctx.send(f"✅ All rules have been removed.")
		else:
			await ctx.send("❌ Safety check not satisfied.")

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.guild)
	@commands.guild_only()
	@checks.is_admin()
	async def editActionLogRule(self, ctx, rule, filteringOption, newAll: bool, newInverse: bool, *newIds: list):
		"""Edit the filtering options of an action log rule."""
		try:
			newIds = [int(id) for id in newIds]
		except:
			await ctx.send("❌ `ids` must be numbers.")
		else:
			guild_data = db.get_guild(ctx.guild.id)
			if not rule in guild_data["action_log"]["actions"]:
				await ctx.send(f"❌ `{rule}` is not an enabled rule.")
			else:
				if not filteringOption in guild_data["action_log"]["actions"][rule]:
					await ctx.send(f"❌ `{filteringOption}` is not a filtering option for `{rule}`.")
				else:
					guild_data["action_log"]["actions"][rule][filteringOption]["all"] = newAll
					guild_data["action_log"]["actions"][rule][filteringOption]["inverse"] = newInverse
					guild_data["action_log"]["actions"][rule][filteringOption]["ids"] = newIds
					db.set_guild(ctx.guild.id, guild_data)
					await ctx.message.add_reaction("✅")

	@commands.Cog.listener()
	async def on_raw_message_delete(self, payload):
		rule_data = await self.rule_check("message_deleted", payload.guild_id)
		if rule_data:
			channel_check = await self.check_data(payload.channel_id, rule_data["channels"])
			cache_check = bool(payload.cached_message)
			if cache_check:
				member_check = await self.check_data(payload.cached_message.author.id, rule_data["members"])
			else:
				member_check = True

			if channel_check and member_check:
				if cache_check:
					content = payload.cached_message.content
					embeds = payload.cached_message.embeds
					author = payload.cached_message.author.mention
					attachments = payload.cached_message.attachments
					log = ["Message Deleted", ""]

					if content:
						if len(content) > 500:
							content = content[:500] + "..."
						log[1] = f"`Content:` {content}"
					elif embeds:
						log[1] = "`Content: [Embed]"

					log[1] = log[1] + f"\n`Author:` {author}\n`Channel:` <#{payload.channel_id}>"
					if attachments:
						attachment_urls = [attachment.url for attachment in attachments]
						urls = ", ".join(attachment_urls)
						if len(urls) > 500:
							urls = urls[:500] + "..."
						log[1] = log[1] + f"\n`Attachments:` {urls}"
				else:
					log = ["Message Deleted", f"`Content/Author:` Unknown (Likely Old Message)\n`Channel:` <#{payload.channel_id}>"]
				await self.enqueue_log(payload.guild_id, log)

	@commands.Cog.listener()
	async def on_raw_bulk_message_delete(self, payload):
		rule_data = await self.rule_check("bulk_message_deleted", payload.guild_id)
		if rule_data:
			channel_check = await self.check_data(payload.channel_id, rule_data["channels"])
			if channel_check:
				member_list = []
				for message_id in payload.message_ids:
					for message in payload.cached_messages:
						if message.id == message_id:
							if not message.author.mention in member_list:
								member_list.append(message.author.mention)
				if member_list:
					members = ", ".join(member_list)
					log = ["Bulk Messages Deleted", f"`Authors:` {members}\n`Channel:` <#{payload.channel_id}>"]
				else:
					log = ["Bulk Messages Deleted", f"`Authors:` Unknown (Likely Old Messages)\n`Channel:` <#{payload.channel_id}>"]
				await self.enqueue_log(payload.guild_id, log)

	@commands.Cog.listener()
	async def on_raw_message_edit(self, payload):
		rule_data = await self.rule_check("message_edited", payload.guild_id)
		if rule_data:
			channel_check = await self.check_data(payload.channel_id, rule_data["channels"])
			cache_check = bool(payload.cached_message)
			if cache_check:
				member_check = await self.check_data(payload.cached_message.author.id, rule_data["members"])
			else:
				member_check = True

			if channel_check and member_check:
				jump_url = self.jump_link.format(guild=payload.guild_id, channel=payload.channel_id, message=payload.message_id)
				changes = {"content": payload.data["content"], "embed": payload.data["embeds"], "attachments": payload.data["attachments"]}
				changes_str = ""
				if changes["content"]:
					changes_str = changes_str + f"`New Content:` {changes['content']}"
				elif changes["embed"]:
					changes_str = changes_str + "`New Content:` [Embed]"
				if changes["attachments"]:
					attachment_urls = [attachment["url"] for attachment in changes["attachments"]]
					urls = ", ".join(attachment_urls)
					if len(urls) > 250:
						urls = urls[:250] + "..."
					changes_str = changes_str + f"\n`New Attachments:` {urls}"
				
				if cache_check:
					before_changes_str = ""
					if changes["content"]:
						before_changes_str = before_changes_str + f"`Old Content:` {payload.cached_message.content}"
					if changes["embed"]:
						before_changes_str = before_changes_str + f"`Old Embed:` {'[Embed]' if payload.cached_message.embed else ''}"
					if changes["attachments"]:
						attachment_urls = [attachment.url for attachment in payload.cached_message.attachments]
						urls = ", ".join(attachment_urls)
						if len(urls) > 250:
							urls = urls[:250] + "..."
						before_changes_str = before_changes_str + f"\n`Old Attachments:` {urls}"
					log = ["Message Edited", f"{before_changes_str}\n{changes_str}\n`Author:` {payload.cached_message.author.mention}\n`Channel:` <#{payload.channel_id}>\n[[Jump to Message]]({jump_url})"]
				else:
					log = ["Message Edited", f"{changes_str}\n`Author:` Unknown (Likely Old Message)\n`Channel:` <#{payload.channel_id}>\n[[Jump]]({jump_url})"]
				await self.enqueue_log(payload.guild_id, log)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		rule_data = await self.rule_check("reaction_added", payload.guild_id)
		if rule_data:
			channel_check = await self.check_data(payload.channel_id, rule_data["channels"])
			member_check = await self.check_data(payload.user_id, rule_data["members"])
			if channel_check and member_check:
				jump_url = self.jump_link.format(guild=payload.guild_id, channel=payload.channel_id, message=payload.message_id)
				log = ["Reaction Added", f"`Reaction:` {str(payload.emoji)}\n`Author:` <@{payload.user_id}>\n`Channel:` <#{payload.channel_id}>\n[[Jump to Message]]({jump_url})"]
				await self.enqueue_log(payload.guild_id, log)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		rule_data = await self.rule_check("reaction_removed", payload.guild_id)
		if rule_data:
			channel_check = await self.check_data(payload.channel_id, rule_data["channels"])
			member_check = await self.check_data(payload.user_id, rule_data["members"])
			if channel_check and member_check:
				jump_url = self.jump_link.format(guild=payload.guild_id, channel=payload.channel_id, message=payload.message_id)
				log = ["Reaction Removed", f"`Reaction:` {str(payload.emoji)}\n`Author:` <@{payload.user_id}>\n`Channel:` <#{payload.channel_id}>\n[[Jump to Message]]({jump_url})"]
				await self.enqueue_log(payload.guild_id, log)

	@commands.Cog.listener()
	async def on_raw_reaction_clear(self, payload):
		rule_data = await self.rule_check("reactions_cleared", payload.guild_id)
		if rule_data:
			channel_check = await self.check_data(payload.channel_id, rule_data["channels"])
			if channel_check:
				jump_url = self.jump_link.format(guild=payload.guild_id, channel=payload.channel_id, message=payload.message_id)
				log = ["Reactions Cleared", f"`Channel:` <#{payload.channel_id}>\n[[Jump to Message]]({jump_url})"]
				await self.enqueue_log(payload.guild_id, log)

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		rule_data = await self.rule_check("channel_created", channel.guild.id)
		if rule_data:
			jump_url = self.jump_link.format(guild=channel.guild.id, channel=channel.id, message=None)
			log = ["Channel Created", f"`Channel:` {channel.mention}\n[[Jump to Channel]]({jump_url})"]
			await self.enqueue_log(channel.guild.id, log)

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		rule_data = await self.rule_check("channel_deleted", channel.guild.id)
		if rule_data:
			channel_check = await self.check_data(channel.id, rule_data["channels"])
			if channel_check:
				log = ["Channel Deleted", f"`Channel Name:` {channel.name}\n`Channel ID:` {channel.id}"]
				await self.enqueue_log(channel.guild.id, log)

	@commands.Cog.listener()
	async def on_guild_channel_update(self, ch_before, ch_after):
		rule_data = await self.rule_check("channel_updated", ch_before.guild.id)
		if rule_data:
			channel_check = await self.check_data(ch_before.id,  rule_data["channels"])
			if channel_check:
				jump_url = self.jump_link.format(guild=ch_after.guild.id, channel=ch_after.id, message=None)
				changes_str = ""
				before_attrs = {attr: getattr(ch_before, attr, None) for attr in dir(ch_before)}
				print("before:", before_attrs, dir(ch_before))
				print("after:", {attr: getattr(ch_after, attr, None) for attr in dir(ch_after)})
				for k, v in before_attrs.items():
					if not k.startswith("_") and not isinstance(v, function):
						before_val = v
						after_val = getattr(ch_after, k, None)
						if before_val != after_val:
							changes_str = changes_str + f"`{k.capitalize()} Before:` {before_val}\n`{k.capitalize()} After:` {after_val}\n"
				changes_str = changes_str[:-1]
				print(changes_str)
				
				log = ["Channel Updated", f"`Channel:` {ch_after.mention}\n{changes_str}\n[[Jump to Channel]]({jump_url})"]
				await self.enqueue_log(ch_after.guild.id, log)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		rule_data = await self.rule_check("member_joined", member.guild.id)
		if rule_data:
			# embed = discord.Embed(
			# 	description = f"{member.mention} (`{member.name}#{member.discriminator}`)\nAccount Age: <t:{member.created_at.timestamp()}:R>",
			# 	colour = discord.Colour.gold()
			# )
			# embed.set_author(name = "Member Joined", icon_url = member.guild.icon_url)
			# embed.set_thumbnail(url = member.avatar_url)
			# embed.set_footer(text = f"ID: {member.id}")
			# embed.timestamp = datetime.datetime.now()

			# await self.send_log(member.guild, embed)

			log = ["Member Joined", f"`Member:` {member.mention} ({member.name}#{member.discriminator})\n`Account Age:` <t:{member.created_at.timestamp()}:R>\n`ID:` {member.id}"]
			await self.enqueue_log(member.guild.id, log)

	@commands.Cog.listener()
	async def on_member_leave(self, member):
		rule_data = await self.rule_check("member_left", member.guild.id)
		if rule_data:
			role_str = " ".join([role.mention for role in member.roles])
		# 	embed = discord.Embed(
		# 		description = f"{member.mention} (`{member.name}#{member.discriminator}`)\nRoles: {role_str}",
		# 		colour = discord.Colour.gold()
		# 	)
		# 	embed.set_author(name = "Member Left", icon_url = member.guild.icon_url)
		# 	embed.set_thumbnail(url = member.avatar_url)
		# 	embed.set_footer(text = f"ID: {member.id}")
		# 	embed.timestamp = datetime.datetime.now()
			
		# 	await self.send_log(member.guild, embed)

			log = ["Member Left", f"`Member:` {member.mention} ({member.name}#{member.discriminator})\nRoles: {role_str}\n`ID:` {member.id}"]
			await self.enqueue_log(member.guild.id, log)

	@commands.Cog.listener()
	async def on_member_ban(self, guild, member):
		rule_data = await self.rule_check("member_banned", guild.id)
		if rule_data:
			log = ["Member Banned", f"`Member:` {member.mention} ({member.name}#{member.discriminator})\n`ID:` {member.id}"]
			await self.enqueue_log(guild.id, log)

	@commands.Cog.listener()
	async def on_member_unban(self, guild, member):
		rule_data = await self.rule_check("member_unbanned", guild.id)
		if rule_data:
			log = ["Member Unbanned", f"`Member:` {member.mention} ({member.name}#{member.discriminator})\n`ID:` {member.id}"]
			await self.enqueue_log(guild.id, log)

	@commands.Cog.listener()
	async def on_member_update(self, mem_before, mem_after):
		rule_data = await self.rule_check("member_updated", mem_before.guild.id)
		if rule_data:
			member_check = await self.check_data(mem_before.id, rule_data["members"])
			if member_check:
				changes_str = ""
				before_attrs = {attr: getattr(mem_before, attr, None) for attr in mem_before.__slots__}
				for k, v in before_attrs.items():
					if not k.startswith("_"):
						before_val = v
						after_val = getattr(mem_after, k, None)
						if before_val != after_val:
							if k == "roles":
								if len(before_val) > len(after_val):
									removed_roles = ", ".join([role.mention for role in before_val if not role in after_val])
									changes_str = f"`Roles Removed:` {removed_roles}\n"
								else:
									added_roles = ", ".join([role.mention for role in after_val if not role in before_val])
									changes_str = f"`Roles Added:` {added_roles}\n"
							elif k == "activities":
								if before_val:
									before_val = before_val[0]
								if after_val:
									after_val = after_val[0]
								activity_type_before = type(before_val)
								activity_type_after = type(after_val)
								print("type:", activity_type_before, activity_type_after)
								if activity_type_before in self.activity_types:
									activ_before = f"{self.activity_types[activity_type_before].capitalize()} {getattr(before_val, 'name', '')}"
								else:
									activ_before = f"{getattr(before_val, 'name', 'None')}"
								if activity_type_after in self.activity_types:
									activ_after = f"{self.activity_types[activity_type_after].capitalize()} {getattr(after_val, 'name', '')}"
								else:
									activ_after = f"{getattr(after_val, 'name', 'None')}"
								changes_str += f"`Activity Before:` {activ_before}\n`Activity After:` {activ_after}\n"
							elif k == "status":
								changes_str += f"`Status Before:` {before_val}\n`Status After:` {after_val}\n"
							elif k == "nick":
								changes_str = f"`Nickname Before:` {before_val}\n`Nickname After:` {after_val}\n"
							else:
								changes_str += f"`{k.capitalize()} Before:` {before_val}\n`{k.capitalize()} After:` {after_val}\n"
							changes_str = changes_str[:-1]

				if changes_str:
					log = ["Member Updated", f"`Member:` {mem_after.mention}\n{changes_str}"]
					await self.enqueue_log(mem_after.guild.id, log)

	@commands.Cog.listener()
	async def on_guild_role_create(self, role):
		rule_data = await self.rule_check("role_created", role.guild.id)
		if rule_data:
			colour_hex = "{0:02x}{1:02x}{2:02x}".format(role.colour.r, role.colour.g, role.colour.b)
			# embed = discord.Embed(
			# 	description = f"{role.mention}\n`Colour:` #{colour_hex}",
			# 	colour = role.colour
			# )
			# embed.set_author(name = "Role Created", icon_url = role.guild.icon_url)
			# embed.set_thumbnail(url = f"https://singlecolorimage.com/get/{colour_hex}/50x50")
			# embed.set_footer(text = f"ID: {role.id}")
			# embed.timestamp = datetime.datetime.now()

			# await self.send_log(role.guild, embed)

			log = ["Role Created", f"`Role:` {role.mention}\n`Colour:` #{colour_hex}\n`ID:` {role.id}"]
			await self.enqueue_log(role.guild.id, log)

	@commands.Cog.listener()
	async def on_guild_role_delete(self, role):
		rule_data = await self.rule_check("role_deleted", role.guild.id)
		if rule_data:
			colour_hex = "{0:02x}{1:02x}{2:02x}".format(role.colour.r, role.colour.g, role.colour.b)
			# embed = discord.Embed(
			# 	description = f"{role.mention}\n`Colour: ` #{colour_hex}",
			# 	colour = role.colour
			# )
			# embed.set_author(name = "Role Deleted", icon_url = role.guild.icon_url)
			# embed.set_thumbnail(url = f"https://singlecolorimage.com/get/{colour_hex}/50x50")
			# embed.set_footer(text = f"ID: {role.id}")
			# embed.timestamp = datetime.datetime.now()

			# await self.send_log(role.guild, embed)

			log = ["Role Deleted", f"`Role:` {role.mention}\n`Colour:` #{colour_hex}\n`ID:` {role.id}"]
			await self.enqueue_log(role.guild.id, log)

	@commands.Cog.listener()
	async def on_guild_role_update(self, role_before, role_after):
		rule_data = await self.rule_check("role_updated", role_after.guild.id)
		if rule_data:
			role_check = await self.check_data(role_after.id, rule_data["roles"])
			if role_check:
				changes_str = ""
				before_attrs = {attr: getattr(role_before, attr, None) for attr in role_before.__slots__}
				for k, v in before_attrs.items():
					if not k.startswith("_"):
						before_val = v
						after_val = getattr(role_after, k, None)
						if before_val != after_val:
							if k == "color" or k == "name" or k == "hoist" or k == "mentionable" or k == "position":
								if k == "color":
									before_val = "{0:02x}{1:02x}{2:02x}".format(before_val.r, before_val.g, before_val.b)
									after_val = "{0:02x}{1:02x}{2:02x}".format(after_val.r, after_val.g, after_val.b)
								changes_str += f"`{k.capitalize()} Before:` {before_val}\n`{k.capitalize()} After:` {after_val}\n"
							elif k == "permissions":
								before_perms = filter(lambda perm: perm[0] if perm[1] else "", iter(before_val))
								after_perms = filter(lambda perm: perm[0] if perm[1] else "", iter(after_val))
								if len(before_perms) > len(after_perms):
									removed_permissions = ", ".join([perm for perm in before_perms if not perm in after_perms])
									changes_str += f"`Permissions Removed:` {removed_permissions}\n"
								else:
									added_permissions = ", ".join([perm for perm in after_perms if not perm in before_perms])
									changes_str += f"`Permissions Removed:` {added_permissions}\n"
				if changes_str:
					changes_str = changes_str[:-1]
					log = ["Role Updated", f"`Role:` {role_after.mention}\n{changes_str}"]
					# Possibly add an optional argument to modify embed properties
					await self.enqueue_log(role_after.guild.id, log)

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, voice_before, voice_after):
		rule_data = await self.rule_check("voice_activity_changed", member.guild.id)
		if rule_data:
			member_check = await self.check_data(member.id, rule_data["members"])
			if member_check:
				changes_str = ""
				before_attrs = {attr: getattr(voice_before, attr, None) for attr in voice_before.__slots__}
				for k, v in before_attrs.items():
					if not k.startswith("_"):
						before_val = v
						after_val = getattr(voice_after, k, None)
						if before_val != after_val:
							changes_str = changes_str + f"`{k.capitalize()} Before:` {before_val}\n`{k.capitalize()} After:` {after_val}\n"
				changes_str = changes_str[:-1]
				log = ["Member Voice Status Changed", f"`Member:` {member.mention}\n{changes_str}"]
				await self.enqueue_log(member.guild.id, log)

	@commands.Cog.listener()
	async def on_invite_create(self, invite):
		rule_data = await self.rule_check("invite_created", invite.guild.id)
		if rule_data:
			if isinstance(invite.channel, discord.abc.GuildChannel) or isinstance(invite.channel, discord.PartialInviteChannel):
				channel = invite.channel.mention
			else:
				channel = f"<#{invite.channel.id}>"
			log = ["Invite Created", f"`Inviter:` {invite.inviter}\n`Channel:` {channel}\n`Link:` {invite.url}\n"]
			await self.enqueue_log(invite.guild.id, log)

	@commands.Cog.listener()
	async def on_invite_delete(self, invite):
		rule_data = await self.rule_check("invite_deleted", invite.guild.id)
		if rule_data:
			if isinstance(invite.channel, discord.abc.GuildChannel) or isinstance(invite.channel, discord.PartialInviteChannel):
				channel = invite.channel.mention
			else:
				channel = f"<#{invite.channel.id}>"
			log = ["Invite Deleted", f"`Channel:` {channel}\n`Link:` https://discord.com/{invite.code}"]
			await self.enqueue_log(invite.guild.id, log)

def setup(client):
	client.add_cog(action_log(client))
