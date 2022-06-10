from config import bot
from dames_files.classes.Jeu import Jeu

import asyncio
import nest_asyncio
nest_asyncio.apply()

async def affiche(msg,messageAEdit):
    await messageAEdit.edit(content=msg)

async def prompt(ctx,joueur : str = False):
    channelBon = False
    bonJoueur = False
    while (not channelBon) or (not bonJoueur) :
        channelBon = False
        bonJoueur = False        
        loop = asyncio.get_event_loop()
        coroutine  = bot.wait_for("message")
        msgDiscord = loop.run_until_complete(coroutine)
        channelBon = msgDiscord.channel == ctx.channel
        # if  joueur :
            # bonJoueur = msgDiscord.author.display_name == joueur
        # else:
        bonJoueur = msgDiscord.author.display_name != ctx.me.display_name
        
        if channelBon and bonJoueur:
            msg = msgDiscord.content.strip()
            await msgDiscord.delete()
            return msg
        else:
            print("\tmauvaise personne concenée")
    print("ERREUR INTERNE : dans prompt")

async def identification(ctx) -> str:
    channelBon = False
    bonJoueur = False
    while (not channelBon) or (not bonJoueur) :
        channelBon = False
        bonJoueur = False        
        loop = asyncio.get_event_loop()
        coroutine  = bot.wait_for("message")
        msgDiscord = loop.run_until_complete(coroutine)
        channelBon = msgDiscord.channel == ctx.channel
        bonJoueur = msgDiscord.author.display_name != ctx.me.display_name
        if channelBon and bonJoueur:
            joueur = msgDiscord.author.display_name
            print(f"joueur {joueur} qui a envoyé \"{msgDiscord.content}\"")
            await msgDiscord.delete()
            return joueur
    print("ERREUR INTERNE : dans identification")    

@bot.command(aliases = ["dame"])
async def dames(ctx, Arg = None):
    msgAccueil = f"""
        **Jeu des dames** version **bêta**
        **Mode débug :** ```
         - n'importe qui peut jouer à la place du joueur concerné
         - les réactions ne sont pas implémentées : tout ce passe par message envoyé dans ce channel
         - Mais une partie peut (normalement) être débutée, stoppée, reprise et finie !```
        **Liste des bugs:**```
         - S'il vous reste plus qu'un pion et qu'il ne peut pas bouger : la partie est bloquée```
        *Si vous constatez des bugs: allez raler auprès d'Alexis*
        """
    messageAEdit = await ctx.channel.send(msgAccueil)
    if Arg == "load" or Arg == "reprendre" :
        jeu = Jeu(affiche,prompt,messageAEdit,ctx)
        jeu.chargementJeu()
        jeu.commenceJeu()
        await ctx.channel.send("Fin du programme")
    elif Arg == "new" or Arg == "nouveau" :
        j1 = None
        j2 = None
        await affiche("joueur 1, identifiez vous en envoyant un message lambda ci-dessous",messageAEdit)
        j1 = await identification(ctx)
        await affiche("joueur 2, identifiez vous en envoyant un message lambda ci-dessous",messageAEdit)
        j2 = await identification(ctx)
        jeu = Jeu(affiche,prompt,messageAEdit,ctx)
        jeu.nouvellePartie(j1,j2)
        jeu.commenceJeu()
        await ctx.channel.send("Fin du programme")

    else:
        regles = f"""
        **Utilisation de la commande** :
        `/dames new` ou `/dames nouveau` : **créer une nouvelle partie**
        \t*Attention : si les 2 nouveaux joueurs avaient déjà une partie en leur nom, elle sera écrasée*
        `/dames load` ou `/dames reprendre` : **reprendre une partie**
        
        Pour **stopper la partie**:\n\ttapez `exit`. Chaque tour est *sauvegardé automatiquement*
        Pour **choisir une case** :\n\ttapez la lettre de la ligne et le numéro de la colonne, par exemple `J3` ou `a10` ...
        Pour **changer de pion sélectionné** :\n\ttapez n'importe quoi, le jeu va ne va pas trouver la case de destination et vous devrez choisir de nouveau le pion à déplacer.
        Pour **manger en rafle** :\n\ttapez la liste des cases de destination séparés par une *virgule* sans espacement, par exemple `e2,C4` ou `E10,G8,e6` ...
        """
        await affiche(msgAccueil + regles,messageAEdit)