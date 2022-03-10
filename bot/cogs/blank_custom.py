# MAKE A COPY OF THIS FILE AND RENAME TO "custom.py" FOR USAGE
# THIS FILE WILL NOT BE RECOGNIZED WITH CURRENT NAME
from discord.ext import commands

class custom(commands.Cog, name = "Custom"):
	"""Custom Commands."""

	def __init__(self, client):
		self.client = client

def setup(client):
	client.add_cog(custom(client))
