import discord
from discord.ext import commands
from database.db import Database as db

def isAdmin():
	async def predicate(ctx):
		valid_roles = db.get_guild(ctx.guild.id)["admin_roles"]
		if not valid_roles:
			return await commands.has_permissions(administrator = True).predicate(ctx)
		else:
			return await commands.has_permissions(administrator = True).predicate(ctx) or await commands.has_any_role(valid_roles).predicate(ctx)
	return commands.check(predicate)

def isMod():
	async def predicate(ctx):
		valid_roles = db.get_guild(ctx.guild.id)["mod_roles"]
		if not valid_roles:
			return False
		else:
			return await commands.has_any_role(valid_roles).predicate(ctx)
	return commands.check(predicate)
