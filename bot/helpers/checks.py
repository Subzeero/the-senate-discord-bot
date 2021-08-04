from discord.ext import commands
from database.db import Database as db

def is_admin():
	async def predicate(ctx):
		valid_roles = db.get_guild(ctx.guild.id)["admin_roles"]
		if valid_roles:
			return await commands.has_permissions(administrator = True).predicate(ctx) or await commands.has_any_role(valid_roles).predicate(ctx)
		else:
			return await commands.has_permissions(administrator = True).predicate(ctx)
	return commands.check(predicate)

def is_mod():
	async def predicate(ctx):
		valid_roles = db.get_guild(ctx.guild.id)["mod_roles"]
		if valid_roles:
			return await commands.has_any_role(valid_roles).predicate(ctx)
		else:
			return False
	return commands.check(predicate)
