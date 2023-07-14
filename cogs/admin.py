from modules.main import is_diceonmat, notDiceOnMatEmbed
from pathlib import Path

import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands

class AdminCog(commands.Cog, name='admin'):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='say', description='用咲希說話')
    async def say(self, interaction: Interaction, message: str):
        diceonmat = await is_diceonmat(interaction)
        if diceonmat == True:
            await interaction.response.send_message('Success!', ephemeral=True)
            await interaction.channel.send(message)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))