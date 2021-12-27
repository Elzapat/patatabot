#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
from aperoV2_files.apero_class import Apero
from aperoV2_files.requete import requete
from aperoV2_files.traitement_args import *
import typed_dotenv

# constantes d'environnement
env = typed_dotenv.load(".env")
APEROV2_MAN_URL = env["APEROV2_MAN_URL"]
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
@bot.command(name="apero ", aliases=["soirée"])
async def aperoV2(ctx, *args):
# def aperoV2(args):

    cmd = None
    if args == None:
        ctx.send("vous avez rien écrit !")
    if type(args) is list:
        cmd = ' '.join(args)
    elif type(args) is str:
        cmd = args
    if "help" or "?" in cmd :
            # print(APEROV2_MAN_URL)
            ctx.send(APEROV2_MAN_URL)
            return


    pos = decomposer_cmd(cmd)
    apero_obj = enregistrer_arguments(cmd, pos)
    apero_obj.affiche_brut()
    status = requete(apero_obj)
    # print(json.dumps(status, indent=4))

    if str(status["status_code"])[0] != "2":
        ctx.send("ERREUR : la requête a échoué ¯\_(ツ)_/¯ ")
    else:
        ctx.send(f"{ctx.author} a rajouté un nouvel apéro : allez donc checker les événements discord et indiquer si vous êtes intéressés 😁")

if __name__ == "__main__":
    # cmd = "/apero chez sam   mercredi le 15 janvier 2022 a 18h30 pour boire"
    # cmd = "/apero chez sam mercredi à 18h30 pour boire"
    # cmd = "/apero pour boire chez sam à 18h31 le 14 janvier"
    cmd = "/apero chez Mael et Alexis à 19:54 le 31 pour fêter le nouvel an help"    
    aperoV2(cmd)