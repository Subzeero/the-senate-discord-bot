import discord
from discord.ext import commands
import database as db

class Testing(commands.Cog):
	"""Internal testing."""

	def __init__(self, client):
		self.client = client

	async def cog_check(self, ctx):
		return commands.is_owner()

def setup(client):
	client.add_cog(Testing(client))