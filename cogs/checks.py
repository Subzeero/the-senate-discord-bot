import discord
from discord.ext import commands

class Checks(commands.Cog):
	"""Internal command checks."""

	def __init__(self, client):
		self.client = client

def setup(client):
	client.add_cog(Checks(client))