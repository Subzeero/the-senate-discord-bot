import discord
from discord.ext import commands
import database as db

class Testing(commands.Cog):
	"""Internal testing."""

	def __init__(self, client):
		self.client = client

	# for key in db.get_keys():
	# 	print(key)
	# 	print(db.get(key))
	# Hello There

def setup(client):
	client.add_cog(Testing(client))
