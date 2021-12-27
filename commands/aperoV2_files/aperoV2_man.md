# ajout d'un événement discord via la commande /apero
## utilisation
### exemples d'utilisation :
```
    /apero chez sam   mercredi le 15 janvier 2022 a 18h30 pour faire du amogus
    /apero chez l'araignée mercredi à 18h30 pour se percher
    /apero chez auriane à 18h31 le 14 janvier pour boire
    /apero chez Mael et Alexis à 18:32 le 31 pour fêter le nouvel an
    /apero help
    /apero ?
```
### Mots-clefs détectés : 
 1. **Hébergeur** : avec le mot-clef `chez`
 2. **jour de la semaine** : si le jour est écrit sans fautes
 3. **date**  : 
    1. avec le mot-clef `le`
    2.  surpasse le jour de la semaine : c'est à dire que si la date notée ne correspond pas au jour de la semaine donnée, ignore le jour de la semaine. 
    3.  on peut marquer le jour , le mois (en lettres ou chiffre) , une libraire fait la détection automatique. Si la commande n'a pas fonctionnée, c'est que la librairie n'a pas compris le format de la date donné (faut vraiment le vouloir !)
 4.  **l'heure** avec `à` ou `a`. l'heure s'écrit `hh`h`mm` ou `hh`:`mm` , pas autrement. Minutes obligatoires.
 5.  **La raison / description** avec `pour` obligatoirement en fin de phrase
## Prérequis
### bibliothèques python
```
json
requests
typed_dotenv
dateparser
```
Note : `typed_dotenv` sert juste à lire des fichiers .env , une autre librairie comme *dotenv* peut faire le boulot aussi tant que les instructions sont changées pour correspondre à la bonne lib.

### Authentification
Étant donné que la commande envoie une requête HTTP pour créer l'événement, l'utilisation de la lib discord pour python sert juste à déclencher la commande (et pourquoi pas à envoyer un message de confirmation).

Alors il est nécessaire **d'initialiser ces informations-ci**  dans `commands/aperoV2_files/requete.py` pour que la commande fonctionne bien
 - TOKEN
   Le jeton d'authentification discord (qui est peut être le même que la lib discord python a besoin)
 - BASE_URL
   "https://discord.com/api/v8"
 - GUILD_ID 
   l'id du serveur discord de la patate
Par défaut, ces informations sont dans un *fichier .env* , on peut changer ça pour adapter sur le serveur.

Dans `commands/aperoV2.py` les informations d'environnement sont également utilisés :
 - APEROV2_MAN_URL
   L'URL de la page Github de cette aide

## petits problèmes potentiels

### conflits de commande
la commande /apero est déjà utilisée pour la commande apéro déja existante.
Solutions : 
 1. utiliser une surcharge de fonctions
    si pas d'arguments --> V1, si arguments --> V2
 2. modifier l'apéro V1 et faire un aigullage selon les arguments
    une sorte de surchage à la main
 3. ne pas appeller l'apéroV2 avec `/apero `
    un alias /soirée est prêt à l'emplace mais je serais triste
 4. la Réponse D

### ça fonctionne ?
J'ai testé en local, la requête HTTP part mais je rentre ma chaîne de caractères du msg discord en dur.

J'ai pas essayé d'utiliser discord.py en local car j'ai jamais fait ça et flemme. Donc **les instrutions relatives à discord.py n'ont pas été testées** de mon côté.

## Et sinon comment ça va vous ?
[+ d'infos ici](https://bit.ly/2TuCFfu)
