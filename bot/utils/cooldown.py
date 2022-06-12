from discord.ext import tasks
import time

users_on_cooldown = {}

def get_users_on_cooldown():
	return users_on_cooldown

def get_user_time(user_id):
	cooldown_time = users_on_cooldown[user_id]["time"]
	if cooldown_time == 0:
		return cooldown_time
	else:
		return cooldown_time - time.time()

@tasks.loop(seconds=30)
async def manage_cooldowns():
	users_to_remove = []
	for user, data in users_on_cooldown.items():
		if data["time"] < time.time():
			users_to_remove.append(user)

	for user in users_to_remove:
		users_on_cooldown.pop(user)

async def abide_cooldown(user, ctx, content = None, embed = None):
	user_id = str(user.id)
	if not user_id in users_on_cooldown.keys():
		users_on_cooldown[user_id] = {
			"quota": 0,
			"time": 0
		}
	
	if users_on_cooldown[user_id]["quota"] < 3 and users_on_cooldown[user_id]["time"] == 0:
		users_on_cooldown[user_id]["quota"] += 1
		if users_on_cooldown[user_id]["quota"] == 3:
			users_on_cooldown[user_id]["time"] = time.time() + 20
			if not content:
				content = f"Easy on the spam {user.mention}! Consider yourself ignored for the next while 🙊"
			else:
				content += f"\n\nEasy on the spam {user.mention}! Consider yourself ignored for the next while 🙊"
		await ctx.send(content = content, embed = embed)
