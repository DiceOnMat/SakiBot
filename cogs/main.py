import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands

class MainCog(commands.Cog, name='main'):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(
        name='關於',
        description='有關天馬咲希'
    )
    async def about(self, interaction: discord.Interaction) -> None:    
        embed = Embed(title="天馬咲希 • Tenma Saki",
                      description="**天馬咲希**是由**DiceOnMat(泡泡)**製作的機器人",
                      color=0xFFDD45)
        embed.set_author(name="天馬咲希", url="https://github.com/DiceOnMat/SakiSecretary",
                         icon_url="https://i.imgur.com/IRY7pH0.jpg")
        embed.set_image(url="https://i.imgur.com/i4h0X3D.png")
        embed.set_footer(text=f"天馬咲希 v{self.bot.version} - by DiceOnMat")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="倍率",
        description="計算隊伍技能倍率"
    )
    @app_commands.describe(
        leader = "隊長倍率",
        member1 = "隊員1倍率",
        member2 = "隊員2倍率",
        member3 = "隊員3倍率",
        member4 = "隊員4倍率"
    )
    @app_commands.rename(
        leader = "隊長倍率",
        member1 = "隊員1倍率",
        member2 = "隊員2倍率",
        member3 = "隊員3倍率",
        member4 = "隊員4倍率"
    )
    async def point(
        self,
        interaction: discord.Interaction,
        leader: int,
        member1: int,
        member2: int,
        member3: int,
        member4: int
    ) -> None:
        if any(x <= 0 for x in (leader, member1, member2, member3, member4)):
            return await interaction.response.send_message("請輸入大於0的數字")
        product = float(1 + (leader + (0.2 * (member1 + member2 + member3 + member4))) / 100)
        return await interaction.response.send_message(f"此隊倍率為：{product}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MainCog(bot))