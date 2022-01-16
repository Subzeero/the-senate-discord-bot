from discord.ext import commands
from database.db import Database as db
from utils import cooldown

def is_admin():
	async def predicate(ctx):
		guild_data = db.get_guild(ctx.guild.id)
		valid_roles = guild_data["admin_roles"]
		permissions = ctx.channel.permissions_for(ctx.author)
		if permissions.administrator:
			return True

		roles = ctx.author.roles
		for role in roles:
			if role.id in valid_roles:
				return True
		return False
	return commands.check(predicate)

def is_mod():
	async def predicate(ctx):
		guild_data = db.get_guild(ctx.guild.id)
		valid_roles = guild_data["mod_roles"]
		permissions = ctx.channel.permissions_for(ctx.author)
		if permissions.manage_guild:
			return True

		roles = ctx.author.roles
		for role in roles:
			if role.id in valid_roles:
				return True
		return False
	return commands.check(predicate)

def is_admin_or_mod():
	async def predicate(ctx):
		guild_data = db.get_guild(ctx.guild.id)
		valid_roles = guild_data["admin_roles"] + guild_data["mod_roles"]

		permissions = ctx.channel.permissions_for(ctx.author)
		if permissions.administrator or permissions.manage_guild:
			return True

		roles = ctx.author.roles
		for role in roles:
			if role.id in valid_roles:
				return True
		return False
	return commands.check(predicate)

def is_on_global_cooldown():
	async def predicate(ctx):
		user_id = str(ctx.author.id)
		cooldown_data = cooldown.get_users_on_cooldown()
		if not user_id in cooldown_data.keys():
			return False, 0
		else:
			if cooldown_data[user_id]["quota"] < 3:
				return False, 0
			else:
				return True, cooldown.get_user_time(user_id)
	return commands.check(predicate)
