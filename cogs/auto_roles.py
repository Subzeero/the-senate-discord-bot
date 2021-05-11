import discord
from discord.ext import commands
import database as db

class AutoRoles(commands.Cog):
	"""Internal testing."""

	def __init__(self, client):
		self.client = client

def setup(client):
	client.add_cog(AutoRoles(client))
