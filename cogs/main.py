import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from datetime import datetime
import requests, io, aiohttp


class MainCog(commands.Cog, name='main'):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.TIME_DIFFERENCE = 31539600000

###########################
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

###########################
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

    @app_commands.command(
        name="近期活動",
        description="查詢近期活動資訊"
    )
    @app_commands.describe(
        recent = "今期/下期"
    )
    @app_commands.rename(
        recent = "活動"
    )
    @app_commands.choices(
        recent=[
            app_commands.Choice(name="今期", value="now"),
            app_commands.Choice(name="下期", value="next")
        ]
    )
    async def recent_event(
        self,
        interaction: discord.Interaction, 
        recent: app_commands.Choice[str]
    ):      
        if (recent.value == "now"):
            current_event = requests.get("https://strapi.sekai.best/sekai-current-event-tw").json()['eventJson']
            event_id = current_event['id']
            start_time = datetime.fromtimestamp(current_event['startAt']/1000).strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.fromtimestamp(current_event['aggregateAt']/1000).strftime('%Y-%m-%d %H:%M:%S')
            event_type = "馬拉松" if current_event['eventType'] == "marathon" else "嘉年華"
            event_name = current_event['assetbundleName']
            url = f"https://storage.sekai.best/sekai-assets/home/banner/{event_name}_rip/{event_name}.webp"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await interaction.response.send_message('Banner讀取失敗')
                    data = io.BytesIO(await resp.read())
            return await interaction.response.send_message(f"今期活動為{event_id}期\n活動類型為：{event_type}\n活動開始時間：{start_time}\n活動結束時間：{end_time}\n", file=discord.File(data, f'banner{event_id}.png'))
            
        if (recent.value == "next"):
            current_event = requests.get("https://strapi.sekai.best/sekai-current-event-tw").json()['eventJson']
            event_data = requests.get("https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/events.json").json()
            event_id = (current_event['id'] + 1)
            event = event_data[event_id - 1]
            start_time = datetime.fromtimestamp((event['startAt'] + self.TIME_DIFFERENCE)/1000).strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.fromtimestamp((event['aggregateAt'] + self.TIME_DIFFERENCE)/1000).strftime('%Y-%m-%d %H:%M:%S')
            event_type = "馬拉松" if event['eventType'] == "marathon" else "嘉年華"
            event_name = event['assetbundleName']
            url = f"https://storage.sekai.best/sekai-assets/home/banner/{event_name}_rip/{event_name}.webp"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await interaction.response.send_message('Banner讀取失敗')
                    data = io.BytesIO(await resp.read())
            return await interaction.response.send_message(f"下期活動為{event_id}期\n活動類型為：{event_type}\n活動開始時間：{start_time}\n活動結束時間：{end_time}\n", file=discord.File(data, f'banner{event_id}.png'))
                    
        return await interaction.response.send_message(f"輸入項目錯誤！請重新輸入")

###########################
    @app_commands.command(
        name="活動查詢",
        description="查詢任意一期活動資訊"
    )
    @app_commands.describe(
        id = "活動編號/活動期數"
    )
    @app_commands.rename(
        id = "編號"
    )
    async def find_event(
        self,
        interaction: discord.Interaction, 
        id: int
    ):      
        if (id > 0):
            event_data = requests.get("https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/events.json").json()
            if (id > len(event_data)):
                return await interaction.response.send_message(f"查無此期！請重新輸入")
            event = event_data[id - 1]
            start_time = datetime.fromtimestamp((event['startAt'] + self.TIME_DIFFERENCE)/1000).strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.fromtimestamp((event['aggregateAt'] + self.TIME_DIFFERENCE)/1000).strftime('%Y-%m-%d %H:%M:%S')
            event_type = "馬拉松" if event['eventType'] == "marathon" else "嘉年華"
            event_name = event['assetbundleName']
            url = f"https://storage.sekai.best/sekai-assets/home/banner/{event_name}_rip/{event_name}.webp"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await interaction.response.send_message('Banner讀取失敗')
                    data = io.BytesIO(await resp.read())
            return await interaction.response.send_message(f"此活動為第{id}期\n活動類型為：{event_type}\n活動開始時間：{start_time}\n活動結束時間：{end_time}\n", file=discord.File(data, f'banner{id}.png'))
            

        return await interaction.response.send_message("輸入項目不能少於1！請重新輸入")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MainCog(bot))