#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from commands.apero.apero import Apero

"""
Fonction decomposer_cmd
Entrée :
 -  le message discord
    exemple:
    "/apero chez sam mercredi le 15 janvier 20222 a 18h30 pour boire"
Sortie (return) :
 -  une liste de type d'information analysée (hebergeur, date etc.) et sa position dans la chaîne de caractère
    Si une information n'est pas fournie en entrée : valeur -1
"""

def decomposer_cmd(cmd: str) -> list[tuple]:
    cmd = cmd.lower()
    print(f"commande discord passée : \"{cmd}\"")
    # position (nombre) de où sont situés les informations :
    pos = []

    j_semaines = ['lundi', 'mardi', 'mercredi',
                  'jeudi', 'vendredi', 'samedi', 'dimanche']

    pos.append(("hebergeur", cmd.find("chez ")))
    pos.append(("date", cmd.find("le ")))

    pos_j_semaine = -1
    for j_semaine in (j_semaines):
        pos_j_semaine = cmd.find(j_semaine)
        if pos_j_semaine != -1:
            break
    pos.append(("j_semaine", pos_j_semaine))

    pos_heure = cmd.find("à ")
    if pos_heure == -1:
        pos_heure = cmd.find("a ")
    pos.append(("heure", pos_heure))

    pos.append(("description", cmd.find("pour ")))

    pos = sorted(pos, key=lambda item: item[1])

    return pos


"""
Fonction enregistrer_arguments
Entrée :
 -  la commande discord originale
 -  la position des informations (cf fonction decomposer_cmd)
Sortie : 
 -  un objet Apéro
    Il contient toutes les information stockées dans des champs de l'objet
    par exemple, taper apero.getHebergeur() renverra le nom de chez qui c'est
    voir la classe Apero pour + d'infos
"""


def enregistrer_arguments(cmd: str, pos: list[tuple]) -> Apero:
    apero_obj = Apero()

    # on segmente la commande donnée selon les positions
    # des informations trouvées
    for i in range(0, len(pos)):

        # initialisation, cle est le type (hebergeur, description etc.)
        # et valeur est ce qu'il vaut (chez tel personne par exemple)
        cle = pos[i][0]
        valeur = str
        # valeur -1 = pas d'infos : on zappe
        if pos[i][1] == -1:
            continue

        # on récupère un morceau du msg discord selon sa position
        if i == len(pos)-1:
            valeur = cmd[pos[i][1]:]
        else:
            valeur = cmd[pos[i][1]:pos[i+1][1]-1]

        # on retire les espaces de fin
        while valeur[-1] == " ":
            valeur = valeur[:-1]

        # on retire les mots-clefs "chez" , "à" etc.
        # et on enregistre dans l'objet
        if cle == "hebergeur":
            apero_obj.setHebergeur(valeur[len("chez "):])
        elif cle == "date":
            apero_obj.setMoment("date", valeur[len("le "):])
        elif cle == "j_semaine":
            apero_obj.setMoment(
                "j_semaine", valeur)
        elif cle == "heure":
            apero_obj.setMoment("heure", valeur[len("à "):])
        elif cle == "description":
            apero_obj.setDescription(valeur[len("pour "):])
        else:
            raise ValueError(f" type {cle} dans la list pos non reconnu.")

    return apero_obj
