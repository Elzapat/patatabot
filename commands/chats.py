import os
import random
import interactions
from config import bot, interactions_bot
from discord import File

@bot.command()
async def mitsuki(ctx):
    await ctx.channel.send(file=File("../images/mitsuki/" + random.choice(os.listdir("../images/mitsuki"))))

@bot.command()
async def gaspard(ctx):
    await ctx.channel.send(file=File("../images/gaspard/" + random.choice(os.listdir("../images/gaspard"))))

@bot.command()
async def depression(ctx):
    await ctx.channel.send(file=File("../images/depression/" + random.choice(os.listdir("../images/depression"))))

@bot.command(name="chapeau", aliases=["^^", "benoit", "chapeau-chapeau"])
async def chapeau(ctx):
    await ctx.channel.send(file=File("../images/chapeau/" + random.choice(os.listdir("../images/chapeau"))))

@bot.command(name="catfaceplant", aliases=[":person_facepalming:", "cfp", "facepalm","f","F","catverytired"])
async def catfaceplant(ctx):
    await ctx.channel.send(file=File("../images/catfaceplant/" + random.choice(os.listdir("../images/catfaceplant"))))

@bot.command(name="murphy", aliases=["m", "chaton", "mignon"])
async def murphy(ctx):
    await ctx.channel.send(file=File("../images/murphy/" + random.choice(os.listdir("../images/murphy"))))
