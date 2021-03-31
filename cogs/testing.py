import discord
from discord.ext import commands
import database as db

class Testing(commands.Cog):
	"""Internal testing."""

	def __init__(self, client):
		self.client = client

	print(db.get_keys())

def setup(client):
	client.add_cog(Testing(client))