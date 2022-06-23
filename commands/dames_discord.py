from config import bot, EXIT_DAMES_CODE
from commands.dames.classes.Jeu import Jeu

async def affiche(msg,messageAEdit):
    await messageAEdit.edit(content=msg)

async def prompt(ctx,joueur : str = None, getNickname : bool = False) -> str:
    bonChannel = False
    bonJoueur = False
    while (not bonChannel) or (not bonJoueur) :
        bonChannel = False
        bonJoueur = False        
        msgDiscord  = await bot.wait_for("message")
        bonChannel = msgDiscord.channel == ctx.channel
        # envoi d'un signal d'exit pour les administrateurs
        if bonChannel and msgDiscord.content.strip() == EXIT_DAMES_CODE:
            return "exit"
        if  joueur != None :
            bonJoueur = msgDiscord.author.display_name == joueur
        else:
            bonJoueur = msgDiscord.author.display_name != ctx.me.display_name
        
        if bonChannel and bonJoueur:
            if getNickname:
                joueur = msgDiscord.author.display_name
                await msgDiscord.delete()                
                return joueur
            else:
                msg = msgDiscord.content.strip()
                await msgDiscord.delete()
                return msg
        else:
            print("\tmauvaise personne concenée")
    print("ERREUR INTERNE : dans prompt") 

@bot.command(aliases = ["dame"])
async def dames(ctx, Arg = None):
    argLoad = ["load", "reprendre"]
    argNew = ["new", "nouveau"]

    msgAccueil = f"""
        **Jeu des dames** version **1.0**
        **Liste des bugs:**```
         - S'il vous reste plus qu'un pion et qu'il ne peut pas bouger : la partie est bloquée```
        *Si vous constatez des bugs: allez raler auprès d'Alexis*
        """
    regles = f"""
        **Utilisation de la commande** :
        `/dames new` ou `/dames nouveau` : **créer une nouvelle partie**
        \t*Attention : si les 2 nouveaux joueurs avaient déjà une partie en leur nom, elle sera écrasée*
        `/dames load` ou `/dames reprendre` : **reprendre une partie**
        
        Pour **stopper la partie**:\n\ttapez `exit`. Chaque tour est *sauvegardé automatiquement*
        Pour **choisir une case** :\n\ttapez la lettre de la ligne et le numéro de la colonne, par exemple `J3` ou `a10` ...
        Pour **changer de pion sélectionné** :\n\ttapez n'importe quoi, le jeu va ne va pas trouver la case de destination et vous devrez choisir de nouveau le pion à déplacer.
        Pour **manger en rafle** :\n\ttapez la liste des cases de destination séparés par une *virgule* sans espacement, par exemple `e2,C4` ou `E10,G8,e6` ...
        \n\n** **
        """
    await ctx.channel.send(msgAccueil + regles)
    messageAEdit = await ctx.channel.send("Sortie du jeu de dames de son carton...")

    if not Arg:
        await affiche(f"** **",messageAEdit)
        return

    if Arg not in (argLoad + argNew):
        await affiche(f"Vous avez tapé : `/dames {Arg}`, ça ne permet pas de lancer le jeu",messageAEdit)
    else:
        jeu = Jeu(affiche,prompt,messageAEdit,ctx)
        if Arg in argLoad :
            if await jeu.chargementJeu():
                await jeu.commenceJeu()
        elif Arg in argNew :
            j1 = None
            j2 = None
            await affiche("joueur 1, identifiez vous en envoyant un message lambda ci-dessous",messageAEdit)
            j1 = await prompt(ctx,getNickname=True)
            await affiche("joueur 2, identifiez vous en envoyant un message lambda ci-dessous",messageAEdit)
            j2 = await prompt(ctx,getNickname=True)
            jeu.nouvellePartie(j1,j2)
            await jeu.commenceJeu()
        else:
            await affiche(f"MON CODE EST BOURRÉ : Problème de reconnaissance de l'arguement {Arg} ",messageAEdit)
        await ctx.channel.send("Le jeu de dames est rangé.")
    
