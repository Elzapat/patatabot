import os, random

from config import bot
from discord import File

@bot.command()
async def mitsuki(ctx):
    await ctx.channel.send(file = File("./images/mitsuki/" + random.choice(os.listdir("./images/mitsuki"))))

@bot.command()
async def gaspard(ctx):
    await ctx.channel.send(file = File("./images/gaspard/" + random.choice(os.listdir("./images/gaspard"))))
