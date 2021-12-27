#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
from aperoV2_files.apero_class import Apero
from aperoV2_files.requete import requete
from aperoV2_files.traitement_args import *

"""
TODO:
Axes d'amélioration :
 - voir si la timezone est gênante
 - régler la date de fin afin qu'elle puisse être choise
 - faire un rappel 1h (par exemple) avant le début
 - envoyer un msg de confirmation dès que la commande est réussie
 - gérer les erreurs d'incompréhension de timeparser
"""

"""
Fonction principale :
Entrée : 
 -  la commande / le message discord
Déclencheur : 
 -  "/apéro " (et la suite du message)
    l'espace après est important : je compte sur ça pour pouvoir différencier l'apéroV2 avec l'apéro
Traitement : 
 -  Rajoute un événement discord selon les informations passées
    TODO : avoir un msg du bot de confirmation

# FIXME le "pour" contient la description donc il tout et n'importe quoi : 
# ça pose problème car les mots clefs sont biaisés si le pour est placé en début de commande
"""
# @bot.command(name = "apero ", aliases = ["soirée"])
if __name__ == "__main__":
    # cmd = "/apero chez sam   mercredi le 15 janvier 2022 a 18h30 pour boire"
    # cmd = "/apero chez sam mercredi à 18h30 pour boire"
    # cmd = "/apero pour boire chez sam à 18h31 le 14 janvier"

    cmd = "/apero chez Mael et Alexis à 18h32 le 31 pour fêter le nouvel an"
    pos = decomposer_cmd(cmd)
    apero_obj = enregistrer_arguments(cmd, pos)
    apero_obj.affiche_brut()
    status = requete(apero_obj)
    print(json.dumps(status,indent=4))

    if str(status["status_code"])[0] != "2" :
        print("ERREUR : la requête a échoué ¯\_(ツ)_/¯ ")
    else:
        print("Nouvel apéro : allez donc checker les événements discord et indiquer si vous êtes intéressés 😁")
