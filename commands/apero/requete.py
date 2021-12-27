#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from commands.apero.apero import Apero
from config import TOKEN, BASE_URL, GUILD_ID
import requests
import json

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

def requete(apero_obj: Apero):
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
        "scheduled_start_time": datetime_debut,
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
    print(response)

    json_return = {
        "status_code": response.status_code
    }
    if response.status_code == requests.codes.ok:
        for key, value in response.json().items():
            json_return[key] = value
    else:
        json_return['url'] = url
        json_return['payload'] = payload
    return json_return
