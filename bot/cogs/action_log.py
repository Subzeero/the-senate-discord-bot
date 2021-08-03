import discord
from discord.ext import commands
from database.db import Database as db

class action_log(commands.Cog, name = "Action Log"):
	"""Internal testing."""

	def __init__(self, client):
		self.client = client

def setup(client):
	client.add_cog(action_log(client))
