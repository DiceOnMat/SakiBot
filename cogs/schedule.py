import gspread
from oauth2client.service_account import ServiceAccountCredentials
from table2ascii import table2ascii as t2a, PresetStyle, Alignment

import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands

class ScheduleSystem(discord.ui.View):

    def __init__(self, timeout, user, version):
        super().__init__(timeout=timeout)
        scopes = ["https://spreadsheets.google.com/feeds"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes)
        client = gspread.authorize(credentials)
        sheets = client.open_by_key("1FjYZTwrFoN8RxNZm7dL-TbItubsmsHWI8TT76V0oWj4")
        self.sheets = sheets
        self.user = user
        self.version = version
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            embed = Embed(title="天馬咲希 • 班表系統",
                      description=f"對不起！這個系統是用戶**{self.user}**運行中",
                      color=0xFFDD45)
            embed.set_author(name="天馬咲希",
                            icon_url="https://i.imgur.com/IRY7pH0.jpg")
            embed.set_footer(text=f"天馬咲希 v{self.version} - by DiceOnMat(泡泡)")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        else:
            return True

    async def on_timeout(self):
        embed = Embed(title="天馬咲希 • 班表系統",
                      description="你閑置太久了！自動退出系統",
                      color=0xFFDD45)
        embed.set_author(name="天馬咲希",
                         icon_url="https://i.imgur.com/IRY7pH0.jpg")
        embed.set_footer(text=f"天馬咲希 v{self.version} - by DiceOnMat(泡泡)")
        await self.message.edit(embed=embed, view=None)
        
    @discord.ui.select(
        placeholder = "日期",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(label="0", value=0),
            discord.SelectOption(label="1", value=1),
            discord.SelectOption(label="2", value=2),
        ]
    )
    async def select_callback(self, interaction, select):
        worksheet = self.sheets.get_worksheet(int(select.values[0]))
        list_of_lists = worksheet.get_all_values()
        output = t2a(
            body= [x for x in list_of_lists],
            style=PresetStyle.borderless,
            alignments=[Alignment.CENTER] + [Alignment.CENTER] * (len(list_of_lists[0]) - 1)
        )
        embed = Embed(title="天馬咲希 • 班表系統",
                    description=f"```\n{output}\n```",
                    color=0xFFDD45)
        embed.set_author(name="天馬咲希",
                        icon_url="https://i.imgur.com/IRY7pH0.jpg")
        embed.set_footer(text=f"天馬咲希 v{self.version} - by DiceOnMat(泡泡)")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(row=1, label="報班", style=discord.ButtonStyle.green, custom_id="book")
    async def button1_calllback(self, interaction, button):
        await interaction.response.edit_message(content="報班!", view=self)

    @discord.ui.button(row=1, label="退出", style=discord.ButtonStyle.red, custom_id="exit")
    async def button2_calllback(self, interaction, button):
        embed = Embed(title="天馬咲希 • 班表系統",
                    description="已成功退出系統！感謝使用**天馬咲希**的班表系統",
                    color=0xFFDD45)
        embed.set_author(name="天馬咲希",
                        icon_url="https://i.imgur.com/IRY7pH0.jpg")
        embed.set_footer(text=f"天馬咲希 v{self.version} - by DiceOnMat(泡泡)")
        await interaction.response.edit_message(embed=embed, view=None)

class ScheduleCog(commands.Cog, name='schedule'):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name='班表系統', description='報班/查班')
    async def schedule_system(self, interaction: discord.Interaction) -> None:
        embed = Embed(title="天馬咲希 • 班表系統",
                      description="歡迎使用**天馬咲希**的班表系統",
                      color=0xFFDD45)
        embed.set_author(name="天馬咲希",
                         icon_url="https://i.imgur.com/IRY7pH0.jpg")
        embed.set_footer(text=f"天馬咲希 v{self.bot.version} - by DiceOnMat(泡泡)")
        schedule_view = ScheduleSystem(timeout=30, user=interaction.user, version=self.bot.version)
        await interaction.response.send_message(embed=embed, ephemeral=True, view=schedule_view)
        schedule_view.message = await interaction.original_response()
"""
    @app_commands.command(name='班表', description='有關班表安排')
    async def gsheet(self, interaction: discord.Interaction) -> None:
        scopes = ["https://spreadsheets.google.com/feeds"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes)
        client = gspread.authorize(credentials)
        sheets = client.open_by_key("1FjYZTwrFoN8RxNZm7dL-TbItubsmsHWI8TT76V0oWj4")
        worksheet = sheets.get_worksheet(0)
        list_of_lists = worksheet.get_all_values()
        output = t2a(
            body= [x for x in list_of_lists],
            style=PresetStyle.borderless,
            alignments=[Alignment.CENTER] + [Alignment.LEFT] * (len(list_of_lists[0]) - 1)
        )
        print(output)
        embed = Embed(title="天馬咲希 • Tenma Saki",
                      description=output,
                      color=0xFFDD45)
        embed.set_footer(text=f"天馬咲希 v{self.bot.version} - by DiceOnMat")
        await interaction.response.send_message(f"```\n{output}\n```")
"""
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ScheduleCog(bot))