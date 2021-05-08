import discord
from discord.ext import commands

def isAdmin():
	async def predicate(ctx):
		valid_roles = db.validate_server(ctx.guild.id)["admin_roles"]
		return commands.check_any(commands.has_permissions(administrator), commands.has_any_role(valid_roles))
	return commands.check(predicate)

def isMod():
	async def predicate(ctx):
		valid_roles = db.validate_server(ctx.guild.id)["mod_roles"]
		return commands.has_any_role(valid_roles)
	return predicate
