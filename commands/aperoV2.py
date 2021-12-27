#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from aperoV2_classes.apero_class import Apero
import requests
import json
import typed_dotenv

"""
TODO:
Axes d'amélioration :
 - voir si la timezone est gênante
 - régler la date de fin afin qu'elle puisse être choise
 - faire un rappel 1h (par exemple) avant le début
 - envoyer un msg de confirmation dès que la commande est réussie
 - gérer les erreurs d'incompréhension de timeparser
"""


# constantes d'environnement
env = typed_dotenv.load(".env")
TOKEN = env["DISCORD_TOKEN"]
BASE_URL = env["BASE_URL"]
GUILD_ID = env["GUILD_ID"]


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
def decomposer_cmd(cmd : str) -> list[tuple]:
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
            apero_obj.setDescription( valeur[len("pour "):])
        else:
            raise ValueError(f" type {cle} dans la list pos non reconnu.")

    return apero_obj

"""
Fonction requete
Entrée : 
 -  un objet Apéro où des infos sont enregistrées
Sortie : 
 -  le code de réussite ou d'échec de la requête HTTP
Traitement :
 -  Prépare les informations (payload) dans le format exigé par la boîte aux lettres de discord
 -  Envoie la commande sur le site grâce aux variables d'environnement de connexion et d'URL (des constantes en gros)

"""
def requete(apero_obj : Apero):
    # FIXME régler la timezone, apparemment ça pose pas de souci
    format = "%Y-%m-%dT%H:%M:%S.%f+01:00"

    name = "APÉRO"
    hebergeur = apero_obj.getHebergeur()
    raison = apero_obj.getDescription()
    libelle = f"**{name}** chez **{hebergeur}**"
    if raison:
        libelle += f" pour *{raison}*"
    

    datetime_debut = apero_obj.getMoment().strftime(format)
    datetime_fin = apero_obj.getFin().strftime(format)

    

    url = f"{BASE_URL}/guilds/{GUILD_ID}/scheduled-events"

    payload = json.dumps({
        "channel_id": None,
        "name": name,
        "description": libelle,
        "scheduled_start_time":datetime_debut,
        "scheduled_end_time": datetime_fin,
        "privacy_level": 2,
        "entity_type": 3,
        "entity_metadata": {
            "location": f"chez {hebergeur}"
        }
    })
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json',
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)

    json_return = {
        "status_code" : response.status_code
    }
    if response.status_code == requests.codes.ok:
        for key,value in response.json().items():
            json_return[key] = value 
    else:
        json_return['url'] =url
        json_return['payload'] =payload
    return json_return

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
