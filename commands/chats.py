import os
import random

from config import bot
from discord import File


@bot.command()
async def mitsuki(ctx):
    await ctx.channel.send(file=File("./images/mitsuki/" + random.choice(os.listdir("./images/mitsuki"))))


@bot.command()
async def gaspard(ctx):
    await ctx.channel.send(file=File("./images/gaspard/" + random.choice(os.listdir("./images/gaspard"))))


@bot.command()
async def depression(ctx):
    await ctx.channel.send(file=File("./images/depression/" + random.choice(os.listdir("./images/depression"))))


@bot.command(name="chapeau", aliases=["^^", "benoit", "chapeau-chapeau"])
async def chapeau(ctx):
    await ctx.channel.send(file=File("./images/chapeau/" + random.choice(os.listdir("./images/chapeau"))))


@bot.command(name="catfaceplant", aliases=[":person_facepalming:", "cfp", "facepalm"])
async def catfaceplant(ctx):
    await ctx.channel.send(file=File("./images/catfaceplant/" + random.choice(os.listdir("./images/catfaceplant"))))
