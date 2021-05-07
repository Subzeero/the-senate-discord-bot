import discord

def tempEmbed(*, name = None, desc = None, colour = discord.Colour.gold(), author = None):
	embed = discord.Embed(
		name = name,
		description = desc,
		colour = colour
	)

	embed.set_footer(text = "This message will self-destruct in 10 seconds.")
	if author:
		embed.set_author(
			name = author.name + "#" + author.discriminator,
			icon_url = author.icon_url
		)
	return embed

def infoEmbed(*, name = None, desc = None, colour = discord.Colour.gold(), author = None, footer = None):
	embed = discord.Embed(
		name = name,
		description = desc,
		colour = colour
	)
	if author:
		embed.set_author(
			name = author.name + "#" + author.discriminator,
			icon_url = author.icon_url
		)
	if footer:
		embed.set_footer(text = footer)
	return embed

def customEmbed(*, name = None, desc = None, colour = discord.Colour.gold(), authorName = None, authorIconURL = None, footer = None):
	embed = discord.Embed(
		name = name,
		description = desc,
		colour = colour
	)
	if authorName or authorIconURL:
		embed.set_author(
			name = authorName,
			icon_url = authorIconURL
		)
	if footer:
		embed.set_footer(text = footer)
	return embed
