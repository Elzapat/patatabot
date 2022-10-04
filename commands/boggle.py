from random import randint
import time
import sys

from config import bot

path = "assets/dictionnaire.txt"

motsfrancais = []
file = open(path, 'r')

for ligne in file:
    mot = ligne.strip('\n').upper()
    if len(mot) > 2:
        motsfrancais.append(mot)


def ajouter_mot(dic, mot):
    if mot == '':
        dic['.'] = {}
    else:
        c = mot[0]
        if c not in dic.keys():
            dic[c] = {}
        ajouter_mot(dic[c], mot[1:])


def dictionnaire(L):
    dic = {}
    for mot in L:
        ajouter_mot(dic, mot)
    return dic

motsfrancais = dictionnaire(motsfrancais)


def est_dans(dic, mot):
    if mot == '':
        if '.' in dic.keys():
            return True
        else:
            return False
    else:
        c = mot[0]
        if c not in dic.keys():
            return False
        return est_dans(dic[c], mot[1:])


def tirage(n):
    lettres = ['A', 'A', 'A', 'A', 'A', 'E', 'E', 'E', 'E', 'E', 'I', 'I',
               'I', 'I', 'I', 'O', 'O', 'O', 'O', 'O', 'U', 'U', 'U', 'U',
               'U', 'B', 'B', 'C', 'C', 'D', 'D', 'F', 'F', 'G', 'G', 'H',
               'H', 'L', 'L', 'M', 'M', 'N', 'N', 'P', 'P', 'R', 'R', 'S',
               'S', 'T', 'T', 'K', 'J', 'Q', 'V', 'W', 'X', 'Y', 'Z']
    liste = []
    for i in range(n):
        liste += [lettres[randint(0, 58)]]
    return liste


def grille(n):
    tableau = []
    for i in range(n):
        tableau.append(tirage(n))
    return tableau


def casemot(gr, tab):
    mot = ''
    for x, y in tab:
        mot += gr[x][y]
    return mot


def recherche(G, i, j, dic, tab, n):
    accessibles = [(i-1, j-1), (i-1, j), (i-1, j+1),
                   (i, j-1),             (i, j+1),
                   (i+1, j-1), (i+1, j), (i+1, j+1)]
    liste = []
    mot = casemot(G, tab)
    if '.' in dic:
        liste += [mot]
    for c in accessibles:
        x, y = c
        if x >= 0 and x < n and y >= 0 and y < n and (x, y) not in tab:
            if G[x][y] in dic:
                liste += recherche(G, x, y, dic[G[x][y]], tab+[(x, y)], n)
    return liste


def motsgrille(gr):
    liste = []
    for i in range(len(gr)):
        for j in range(len(gr)):
            liste += recherche(gr, i, j, motsfrancais[gr[i][j]],
                               [(i, j)], len(gr))
    liste.sort()
    liste_finale = [liste[0]]
    for i in range(1, len(liste)):
        if liste[i] != liste_finale[len(liste_finale)-1] and len(liste[i]):
            liste_finale.append(liste[i])
    return liste_finale


@bot.command(name="boggle")
async def boggle(ctx):

    def est_commande(msg):
        return '!' in msg.content

    try:
        if ctx.author.nick is not None:
            texte = '%s joue au Boggle mes frères, encouragez-le !\n```\n' % ctx.author.nick
        else:
            texte = '%s joue au Boggle mes frères, encouragez-le !\n```\n' % ctx.author.name
    except:
        texte = 'Jeu de Boggle :\n```\n'

    temps = 180.0
    gr = grille(4)
    sep = '+'

    message = await ctx.channel.send(texte)

    for i in range(4):
        sep += '---+'
    sep += '\n'
    texte += sep

    for ligne in gr:
        lettres = '| '
        for lettre in ligne:
            lettres += lettre
            lettres += ' | '
        lettres += '\n'
        texte += lettres + sep

    texte += '```'

    mots_trouves = []
    mots = motsgrille(gr)

    deb = time.time()
    while time.time() - deb < temps:

        liste_mots = ''
        for m in mots_trouves:
            liste_mots += '\n' + m

        await message.edit(content=(texte + '\n' +
                           str(int(temps - time.time() + deb)) +
                           ' secondes restantes\n\tPropose un mot avec `!`\n\tTape `!!stop` pour quitter\n' +
                           liste_mots))

        reponse = await bot.wait_for("message", check=est_commande, timeout=180.0)

        if reponse.content == "!!stop":
            await reponse.delete()
            break

        mot = ''
        for lettre in reponse.content.upper():
            if lettre not in '! .':
                mot += lettre

        await reponse.delete()

        if mot in mots and mot not in mots_trouves:
            mots_trouves.append(mot)

    texte += '\nScore : %s%%\n' % (int(len(mots_trouves)/len(mots)*10000)/100)

    texte += '\nMots trouvés :\n'
    mots_trouves.sort()
    for mot in mots_trouves:
        texte += mot + '\t'

    texte += '\n\nMots non trouvés :\n'
    for mot in mots:
        if mot not in mots_trouves:
            texte += mot + '\t'

    await message.edit(content=texte)

