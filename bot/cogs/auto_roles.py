import discord
from discord.ext import commands
from database.db import Database as db

class auto_roles(commands.Cog, name = "Auto Roles"):
	"""Internal testing."""

	def __init__(self, client):
		self.client = client

def setup(client):
	client.add_cog(auto_roles(client))
