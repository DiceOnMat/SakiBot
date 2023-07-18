import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands

class SekaiInfoCog(commands.Cog, name='sekai_info'):
    def __init__(self, bot) -> None:
        self.bot = bot

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SekaiInfoCog(bot))