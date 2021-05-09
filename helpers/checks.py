import discord
from discord.ext import commands
import database as db

def isAdmin():
	async def predicate(ctx):
		valid_roles = db.validate_server(ctx.guild.id)["admin_roles"]
		if not valid_roles:
			return commands.has_permissions(administrator = True)
		else:
			return commands.has_permissions(administrator = True) or commands.has_any_role(valid_roles)
	return commands.check(predicate)

def isMod():
	async def predicate(ctx):
		valid_roles = db.validate_server(ctx.guild.id)["mod_roles"]
		if not valid_roles:
			return False
		else:
			return commands.has_any_role(valid_roles)
	return commands.check(predicate)
