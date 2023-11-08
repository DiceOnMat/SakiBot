import os
import gspread
import time

from modules.main import is_diceonmat, notDiceOnMatEmbed
from pathlib import Path

import discord
from discord import (Game, HTTPException, Intents, Interaction, Message,
                     Status, app_commands)
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')
print(token)

intents = Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True
intents.presences = True

class SakiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=['$'],
            intents=intents
        )
        
    async def setup_hook(self) -> None:
        self.repeat = False
        self.prev = False
        global version
        version = 1.0
        self.version = version

        for filepath in Path('./cogs').glob('**/*.py'):
            cog_name = Path(filepath).stem
            await self.load_extension(f'cogs.{cog_name}')
        await bot.tree.sync()

    async def on_ready(self):
        await self.change_presence(
            status=Status.online,
            activity=Game(name=f'世界計畫')
        )
        print('Bot', f'Logged in as {self.user}')

    async def on_message(self, message: Message):
        if message.author.id == self.user.id:
            return
        await self.process_commands(message)

    async def close(self) -> None:
        return await super().close()

bot = SakiBot()

#unload cog
@bot.command()
async def unload(ctx, extension):
    if await is_diceonmat(ctx):
        await bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Unloaded {extension} done.")

#load cog
@bot.command()
async def load(ctx, extension):
    if await is_diceonmat(ctx):
        await bot.load_extension(f"cogs.{extension}")
        await bot.tree.sync()
        await ctx.send(f"Reloaded {extension} done.")

#reload cog
@bot.command()
async def rl(ctx):
    if await is_diceonmat(ctx):
        for filepath in Path('./cogs').glob('**/*.py'):
            cog_name = Path(filepath).stem
            await bot.reload_extension(f'cogs.{cog_name}')
        await ctx.send(f"Reloaded all cogs done.")

@bot.listen()
async def on_ready():
    task_loop.start() 

@tasks.loop(seconds=1)
async def task_loop():
    pass

bot.run(token)