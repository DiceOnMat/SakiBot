import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands

class MainCog(commands.Cog, name='main'):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name='關於', description='有關天馬咲希')
    async def about(self, interaction: discord.Interaction) -> None:    
        embed = Embed(title="天馬咲希 • Tenma Saki",
                      description="**天馬咲希**是由**DiceOnMat(泡泡)**製作的機器人",
                      color=0xFFDD45)
        embed.set_author(name="天馬咲希", url="https://github.com/DiceOnMat/SakiSecretary",
                         icon_url="https://i.imgur.com/IRY7pH0.jpg")
        embed.set_image(url="https://i.imgur.com/i4h0X3D.png")
        embed.set_footer(text=f"天馬咲希 v{self.bot.version} - by DiceOnMat")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MainCog(bot))