from config import bot
from discord import File

@bot.command(aliases = ["apéro", "Apero"])
async def apero(ctx):
    """
    Appel à tous de se rendre immédiatement chez Samuel pour un Apéro
    """
    await ctx.channel.send(
        """
        **APÉRO CHEZ SAMUEL MAINTENANT**
        """,
        file = File("images/ricard.gif")
    )
