import discord
from discord import Embed, Colour

#diceonmat
async def is_diceonmat(ctx):
    if ctx.message.author.id != 342316999625408513:
        await ctx.reply(embed=notDiceOnMatEmbed(), ephemeral=True)
        return False
    else:
        return True
    
def notDiceOnMatEmbed():
    embed = Embed(title=f'權限不足', description=f'你不是泡泡', color= Colour.from_str('#F13650'))
    embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/1129260804919803906.gif?size=240&quality=lossless')
    return embed