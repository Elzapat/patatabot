#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from discord import File

from config import bot, APERO_MAN_URL
from commands.apero.apero import Apero
from commands.apero.requete import requete
from commands.apero.traitement_args import *

@bot.command(name = "apero", aliases = ["apéro", "Apero", "soirée"])
async def apero(ctx, *args):
    if args:
        await apero_event(ctx, args)
    else:
        await apero_samuel(ctx)

async def apero_samuel(ctx):
    """
    Appel à tous de se rendre immédiatement chez Samuel pour un Apéro
    """
    await ctx.channel.send(
        """
        **APÉRO CHEZ SAMUEL MAINTENANT**
        """,
        file = File("images/ricard.gif")
    )
    
@bot.command(name = "vodka")
async def vodka(ctx):
     await ctx.send(f"T'es malade {ctx.author.mention} on ne boit pas du désinfectant!!!")
    
"""
TODO:
Axes d'amélioration :
 - voir si la timezone est gênante
    -> réglé à +01:00 en dur
 - régler la date de fin afin qu'elle puisse être choisie
 - faire un rappel 1h (par exemple) avant le début
 - envoyer un msg de confirmation dès que la commande est réussie
 - gérer les erreurs d'incompréhension de timeparser
 - avoir la possibilité de mettre le pour autre part qu'à la fin
"""

"""
Fonction principale
Entrée :
 -  la commande / le message discord
Déclencheur :
 -  "/apéro " (et la suite du message)
    l'espace après est important : je compte sur ça pour pouvoir différencier l'apéroV2 avec l'apéro
Traitement :
 -  Rajoute un événement discord selon les informations passées
    TODO : avoir un msg du bot de confirmation
"""
async def apero_event(ctx, *args):
    cmd = None
    if args == None:
        await ctx.send("vous avez rien écrit !")

    if type(args) is list or tuple:
        cmd = ' '.join(args[0])
    elif type(args) is str:
        cmd = args

    if "help" in cmd or "?" in cmd:
        await ctx.send(APERO_MAN_URL)
        return

    pos = decomposer_cmd(cmd)
    apero_obj = enregistrer_arguments(cmd, pos)
    apero_obj.affiche_brut()
    status = requete(apero_obj)

    if str(status["status_code"])[0] != "2":
        print(f"request failed: {status}")
        await ctx.send("ERREUR : la requête a échoué ¯\_(ツ)_/¯ ")
    else:
        await ctx.send(f"{ctx.author.mention} a rajouté un nouvel apéro : allez donc checker les événements discord et indiquer si vous êtes intéressés 😁")

if __name__ == "__main__":
    # cmd = "/apero chez sam   mercredi le 15 janvier 2022 a 18h30 pour boire"
    # cmd = "/apero chez sam mercredi à 18h30 pour boire"
    # cmd = "/apero pour boire chez sam à 18h31 le 14 janvier"
    cmd = "/apero chez Mael et Alexis à 19:54 le 31 pour fêter le nouvel an help"
    apero_event(cmd)
