import json
import asyncio
import random
from pathlib import Path
import sys
import os

ROOT = Path(__file__).parent
TOKENS_FILE = ROOT / "token.json"


def load_tokens(path: Path):
	if not path.exists():
		print("token.json not found; create one with a `tokens` list")
		return [], None
	with open(path, "r", encoding="utf-8") as f:
		data = json.load(f)
	owner = data.get("owner_id")
	if owner is not None:
		try:
			owner = int(owner)
		except Exception:
			owner = None
	return data.get("tokens", []), owner


async def run_bot(token: str, index: int, owner_id: int | None):
	import discord
	from discord.ext import commands

	intents = discord.Intents.default()
	intents.message_content = True
	bot = commands.Bot(command_prefix="~", intents=intents)
	mock_tasks = {}

	@bot.event
	async def on_ready():
		print(f"Bot {index} logged in as {bot.user} (id={bot.user.id})")

	@bot.event
	async def on_command_error(ctx, error):
		from discord.ext.commands import CheckFailure
		if isinstance(error, CheckFailure):
			# Silent ignore for owner check failures (kept for compatibility)
			return
		# Log other errors for debugging
		print("Command error:", error)

	@bot.command(name="ping")
	async def ping(ctx):
		# Simple inline owner check: silently return for non-owners
		if owner_id is not None:
			if ctx.author.id != owner_id:
				return
		else:
			try:
				if not await bot.is_owner(ctx.author):
					return
			except Exception:
				# If owner check fails for any reason, silently ignore
				return
		# Delete invocation so others can't see who ran it (bot needs Manage Messages permission)
		try:
			await ctx.message.delete()
		except Exception:
			pass
		await ctx.send("bulaga")

	@bot.command(name="mock")
	async def mock(ctx, member: discord.Member | None = None, delay: float = 0.1):
		if owner_id is not None:
			if ctx.author.id != owner_id:
				return
		else:
			try:
				if not await bot.is_owner(ctx.author):
					return
			except Exception:
				return

		if member is None:
			member = ctx.message.mentions[0] if ctx.message.mentions else None
		if member is None:
			return

		try:
			delay = int(delay)
		except Exception:
			delay = 0.1
		delay = max(0.1, delay)

		try:
			await ctx.message.delete()
		except Exception:
			pass

		messages = [
			"sana mag bedridden kana",
			"hoy tnaga tanga ano bobo ka",
			"mag bedridden kana sana bobo ka naman",
			"ano bobo tanga ka di makita messages mo",
			"ohohlol ka bobo inutil"
		]

		async def spam():
			while True:
				await ctx.send(f"{member.mention} {random.choice(messages)}")
				await asyncio.sleep(delay)

		if member.id in mock_tasks:
			mock_tasks[member.id].cancel()
			ryase
			pass

		mock_tasks[member.id] = asyncio.create_task(spam())

	@bot.command(name="stop")
	async def stopmock(ctx, member: discord.Member | None = None):
		if owner_id is not None:
			if ctx.author.id != owner_id:
				return
		else:
			try:
				if not await bot.is_owner(ctx.author):
					return
			except Exception:
				return

		if member is None:
			member = ctx.message.mentions[0] if ctx.message.mentions else None
		if member is None:
			return

		if member.id in mock_tasks:
			mock_tasks[member.id].cancel()
			del mock_tasks[member.id]
			try:
				await ctx.message.delete()
			except Exception:
				pass

	try:
		await bot.start(token)
	except Exception as e:
		print(f"Bot {index} stopped: {e}")



async def main():
	tokens, owner_id = load_tokens(TOKENS_FILE)
	if not tokens:
		print("No tokens found in token.json. Exiting.")
		return

	tasks = []
	for i, token in enumerate(tokens, start=1):
		tasks.append(asyncio.create_task(run_bot(token, i, owner_id)))

	# Run until all bots exit (or are cancelled)
	results = await asyncio.gather(*tasks, return_exceptions=True)
	for r in results:
		if isinstance(r, Exception):
			print("One bot exited with:", r)


if __name__ == "__main__":
	# Ensure we run from the project folder so relative paths resolve
	os.chdir(ROOT)
	asyncio.run(main())
