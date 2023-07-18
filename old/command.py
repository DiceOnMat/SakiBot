import discord
from discord import (Game, HTTPException, Intents, Interaction, Message,
                     Status, app_commands)
from discord.ext import commands, tasks

import requests
import aiohttp
import io
import os
import asyncio
import sqlite3
import math

from datetime import datetime
from dotenv import load_dotenv

def run():

    bot = commands.Bot(command_prefix="%", intents=discord.Intents.all())

    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    TIME_DIFFERENCE = 31539600000   
    
    @bot.event
    async def on_ready():
        await bot.change_presence(
            status=Status.online,
            activity=Game(name=f'世界計畫')
        )
        print(f'Logged in as {bot.user}')
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    @bot.tree.command(
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
        interaction: discord.Interaction,
        leader: int,
        member1: int,
        member2: int,
        member3: int,
        member4: int
    ):
        if any(x <= 0 for x in (leader, member1, member2, member3, member4)):
            return await interaction.response.send_message("請輸入大於0的數字")
        product = float(1 + (leader + (0.2 * (member1 + member2 + member3 + member4))) / 100)
        return await interaction.response.send_message(f"此隊倍率為：{product}")


    @bot.tree.command(
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
        interaction: discord.Interaction, 
        recent: app_commands.Choice[str]
    ):  
        await interaction.response.defer() 
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
                        return await interaction.followup.send('Banner讀取失敗')
                    data = io.BytesIO(await resp.read())
            return await interaction.followup.send(f"今期活動為{event_id}期\n活動類型為：{event_type}\n活動開始時間：{start_time}\n活動結束時間：{end_time}\n", file=discord.File(data, f'banner{event_id}.png'))
            
        if (recent.value == "next"):
            current_event = requests.get("https://strapi.sekai.best/sekai-current-event-tw").json()['eventJson']
            event_data = requests.get("https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/events.json").json()
            event_id = (current_event['id'] + 1)
            event = event_data[event_id - 1]
            start_time = datetime.fromtimestamp((event['startAt'] + TIME_DIFFERENCE)/1000).strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.fromtimestamp((event['aggregateAt'] + TIME_DIFFERENCE)/1000).strftime('%Y-%m-%d %H:%M:%S')
            event_type = "馬拉松" if event['eventType'] == "marathon" else "嘉年華"
            event_name = event['assetbundleName']
            url = f"https://storage.sekai.best/sekai-assets/home/banner/{event_name}_rip/{event_name}.webp"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await interaction.followup.send('Banner讀取失敗')
                    data = io.BytesIO(await resp.read())
            return await interaction.followup.send(f"下期活動為{event_id}期\n活動類型為：{event_type}\n活動開始時間：{start_time}\n活動結束時間：{end_time}\n", file=discord.File(data, f'banner{event_id}.png'))
                    
            #for event in event_data:
            #    if event['id'] == event_id:
            #        start_time = datetime.fromtimestamp((event['startAt'] - 31539600000)/1000).strftime('%Y-%m-%d %H:%M:%S')
            #        end_time = datetime.fromtimestamp((event['aggregateAt']- 31539600000)/1000).strftime('%Y-%m-%d %H:%M:%S')
            #        break        
        return await interaction.followup.send(f"輸入項目錯誤！請重新輸入")

    @bot.tree.command(
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
        interaction: discord.Interaction, 
        id: int
    ):
        await interaction.response.defer() 
        if (id > 0):
            event_data = requests.get("https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/events.json").json()
            if (id > len(event_data)):
                return await interaction.followup.send(f"查無此期！請重新輸入")
            event = event_data[id - 1]
            start_time = datetime.fromtimestamp((event['startAt'] + TIME_DIFFERENCE)/1000).strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.fromtimestamp((event['aggregateAt'] + TIME_DIFFERENCE)/1000).strftime('%Y-%m-%d %H:%M:%S')
            event_type = "馬拉松" if event['eventType'] == "marathon" else "嘉年華"
            event_name = event['assetbundleName']
            url = f"https://storage.sekai.best/sekai-assets/home/banner/{event_name}_rip/{event_name}.webp"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await interaction.followup.send('Banner讀取失敗')
                    data = io.BytesIO(await resp.read())
            print(f"此活動為第{id}期\n活動類型為：{event_type}\n活動開始時間：{start_time}\n活動結束時間：{end_time}\n")
            return await interaction.followup.send(f"此活動為第{id}期\n活動類型為：{event_type}\n活動開始時間：{start_time}\n活動結束時間：{end_time}\n", file=discord.File(data, f'banner{id}.png'))           
        return await interaction.followup.send("輸入項目不能少於1！請重新輸入")

    @bot.tree.command(
        name="彈琴",
        description="由天馬咲希演奏"
    )
    @app_commands.describe(
        song = "歌曲"
    )
    @app_commands.rename(
        song = "歌曲"
    )
    @app_commands.choices(
        song=[
            app_commands.Choice(name="[25時、ナイトコードで。] - 再生", value="25_再生"),

            app_commands.Choice(name="[Leo/need] - オーダーメイド", value="ln_オーダーメイド"),

            app_commands.Choice(name="[MORE MORE JUMP!] - マシュマリー", value="mmj_マシュマリー"),

            app_commands.Choice(name="[Vivid BAD SQUAD] - シネマ", value="vbs_シネマ"),

            
            app_commands.Choice(name="[VIRTUAL SINGER] - 初音ミクの激唱", value="vs_初音ミクの激唱"),
            app_commands.Choice(name="[VIRTUAL SINGER] - 星界ちゃんと可不ちゃんのおつかい合騒曲", value="vs_星界ちゃんと可不ちゃんのおつかい合騒曲"),
            app_commands.Choice(name="[VIRTUAL SINGER] - ヤミナベ!!!!", value="vs_ヤミナベ"),
            app_commands.Choice(name="[VIRTUAL SINGER] - What's up? Pop!", value="vs_What's up Pop"),

            app_commands.Choice(name="[Wonderlands×Showtime] - どんな結末がお望みだい", value="ws_どんな結末がお望みだい"),
        ]
    )
    async def play_song(
        interaction: discord.Interaction,
        song: app_commands.Choice[str]
    ):
        if interaction.user.voice is None:
            return await interaction.response.send_message("請進入其中一個語音頻道")
        
        channel = interaction.user.voice.channel
        script_dir = os.path.dirname(os.path.realpath('__file__'))
        sound_file = os.path.join(script_dir + '\\song\\' + song.value + '.mp3')

        if not os.path.exists(sound_file):
            return await interaction.response.send_message("我找不到樂譜")
        
        vc = await channel.connect()
        vc.play(discord.FFmpegPCMAudio(source=sound_file))
        await interaction.response.send_message(f"正在為你彈奏 {song.name}")

        while vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect()
        return

    @bot.tree.command(
        name="唱歌",
        description="由天馬咲希演唱"
    )
    @app_commands.describe(
        song = "歌曲"
    )
    @app_commands.rename(
        song = "歌曲"
    )
    @app_commands.choices(
        song=[
            app_commands.Choice(name="needLe", value="needLe"),
            app_commands.Choice(name="STAGE OF SEKAI", value="STAGE OF SEKAI"),
            app_commands.Choice(name="いかないで", value="いかないで"),
            app_commands.Choice(name="オーダーメイド", value="オーダーメイド"),
            app_commands.Choice(name="カゲロウデイズ", value="カゲロウデイズ"),
            app_commands.Choice(name="タイムマシン", value="タイムマシン"),
            app_commands.Choice(name="テオ", value="テオ"),
            app_commands.Choice(name="てらてら", value="てらてら"),
            app_commands.Choice(name="フロムトーキョー", value="フロムトーキョー"),
            app_commands.Choice(name="夜もすがら君想ふ", value="夜もすがら君想ふ"),
        ]
    )
    async def sing_song(
        interaction: discord.Interaction,
        song: app_commands.Choice[str]
    ):
        channel = interaction.user.voice.channel
        if channel is None:
            return await interaction.response.send_message("請進入其中一個語音頻道")
        
        script_dir = os.path.dirname(os.path.realpath('__file__'))
        sound_file = os.path.join(script_dir + '\\sing\\' + song.value + '.mp3')

        if not os.path.exists(sound_file):
            return await interaction.response.send_message("我找不到歌詞")
        
        vc = await channel.connect()
        vc.play(discord.FFmpegPCMAudio(source=sound_file))
        await interaction.response.send_message(f"正在為你獻唱 {song.name}")

        while vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect()
        return

    rankline = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000]
    @bot.tree.command(
        name="活動分數",
        description="查詢本期活動分數資訊"
    )
    async def recent_event_pt(
        interaction: discord.Interaction, 
    ):
        await interaction.response.defer() 
        output_string = ""
        current_event = requests.get("https://strapi.sekai.best/sekai-current-event-tw").json()['eventJson']
        event_id = current_event['id']
        for rank in rankline:
            json = requests.get(f"https://sekai-world.unipjsk.com/tw/api/user/%7Buser_id%7D/event/{event_id}/ranking?targetRank={rank}").json()['rankings']
            if (json):
                output_string += (f"排名 {rank:>5}：{json[0]['name']:10}   {json[0]['score']:>10} pt\n")

        return await interaction.followup.send(output_string)
    
    @bot.tree.command(
        name="旎袂在哪",
        description="查詢旎袂在哪"
    )
    async def recent_event_pt(
        interaction: discord.Interaction, 
    ):
        await interaction.response.defer() 
        output_string = ""
        conn = sqlite3.connect('./data/events.db')
        c = conn.cursor()
        cursor = c.execute("SELECT RANK, ID, SCORE, NAME from EVENT WHERE ID = 7013445837833394946")
        for row in cursor:
            output_string = (f"找到{row[3]}了！現在是第{row[0]}名，分數為{row[2]}，ID我就不說了")
        conn.close()
        return await interaction.followup.send(output_string)
    # https://sekai-world.unipjsk.com/tw/api/user/7013445837833394946/profile
    import unicodedata
    def wide_chars(s):
        sum = 0
        for x in s:
            if (unicodedata.east_asian_width(x) == 'F' or unicodedata.east_asian_width(x) == 'W' or unicodedata.east_asian_width(x) == 'A'):
                sum = sum + 1
        return sum
    def width(s):
        return len(s) + wide_chars(s)
    
    @bot.tree.command(
        name="群組成員在哪",
        description="查詢群組成員在哪"
    )
    async def recent_event_pt(
        interaction: discord.Interaction, 
    ):
        await interaction.response.defer() 
        output_string = ""
        conn = sqlite3.connect('./data/events.db')
        c = conn.cursor()
        cursor = c.execute("SELECT RANK, ID, SCORE, NAME from EVENT WHERE ID = 7013445837833394946 OR ID = 7072955309194484482 OR ID = 7020368507976162049 OR ID = 7014287943514872577 OR ID = 7038469215585606402 OR ID = 7029991253777586945 OR ID = 7031807681253923585 OR ID = 7031807681253923585 ORDER BY RANK")
        for row in cursor:
            output_string += ("%*s 名次: %*s 分數: %*s\n" % (24-wide_chars(str(row[3])), row[3], 5-wide_chars(str(row[0])), row[0], 10-wide_chars(str(row[2])), row[2]))
        conn.close()
        return await interaction.followup.send(output_string)

    @bot.tree.command(
        name="單場活動分數比較",
        description="計算兩隊不同綜合力和加成打一場所得活動分數的差別（以0火單人AP紅蝦為準並且假設分數受五張四星Lv.1技能影響）"
    )
    @app_commands.describe(
        team1_power = "隊1綜合力",
        team1_bonus = "隊1加成(?%)",
        team2_power = "隊2綜合力",
        team2_bonus = "隊2加成(?%)",
    )
    @app_commands.rename(
        team1_power = "隊1綜合力",
        team1_bonus = "隊1加成",
        team2_power = "隊2綜合力",
        team2_bonus = "隊2加成",
    )
    async def event_point_cmp(
        interaction: discord.Interaction,
        team1_power: float,
        team1_bonus: float,
        team2_power: float,
        team2_bonus: float
    ):
        #活動基本pt：樂曲pt * (100%+個人倍率+隊友倍率) (小數點捨去)

        #個人倍率：每20,000分+1% (小數點捨去) （目前還沒看到上限）
        #隊友倍率：每400,000分+1% (小數點捨去)，最大7%。（隊友平均70萬分則滿倍率）

        #紅蝦 樂曲pt = 100
        if any(x <= 0 for x in (team1_power, team1_bonus, team2_power, team2_bonus)):
            return await interaction.response.send_message("請輸入大於0的數字")
        team1_expect_point = (team1_bonus/100 + 1)*(100 * (1 + 0.01 * math.floor((team1_power*6)/20000)))
        team2_expect_point = (team2_bonus/100 + 1)*(100 * (1 + 0.01 * math.floor((team1_power*6)/20000)))
        best_team = "隊1" if (team1_expect_point >= team2_expect_point) else "隊2"
        return await interaction.response.send_message(f"{best_team}得分比較高所以用{best_team}打活動吧\n隊1所得活動分數為：{math.floor(team1_expect_point)}\n隊2所得活動分數為：{math.floor(team2_expect_point)}\n")

    bot.run(TOKEN)