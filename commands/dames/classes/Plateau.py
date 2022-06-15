from fileinput import filename
from time import sleep
from typing import Tuple
from commands.dames.classes.Pion import Pion
from commands.dames.classes.Case import Case

class Plateau:
    """classe Plateau"""


    def __init__(self,fileName = False) :
        self.__lignes = "ABCDEFGHIJ"
        self.__nbPionsJ1 = 20
        self.__nbPionsJ2 = 20

        self.__cases = self.__initCases__()
        if fileName :
            self.__initPionsSauvegarde__(fileName)
        else:
            self.__initPions__()
    

    def __initCases__(self) -> list[Case]:
        cases = []
        caseClaire = True 
        for ligne in self.__lignes:
            for col in range(1,11):
                cases.append(Case(ligne,col,caseClaire))
                caseClaire = not caseClaire
            caseClaire = not caseClaire
        return cases

    def __initPions__(self):
        # on retire tous les pions s'il y en avait
        for case in self.__cases:
            case.supprPion()
        
        # placement des pions foncés du joueur 2
        i = 0
        nbPions = 0
        while(nbPions<self.__nbPionsJ2):
            if not self.__cases[i].estClaire():
                self.__cases[i].setPion(Pion(2))
                nbPions+=1
            i+=1
        # placement des pions foncés du joueur 1
        i = 0
        nbPions = 0
        length = len(self.__cases) -1
        while(nbPions<self.__nbPionsJ1):
            if not self.__cases[length-i].estClaire():
                self.__cases[length-i].setPion(Pion(1))
                nbPions+=1
            i+=1
    
    def __initPionsSauvegarde__(self,plateauData):
        # on initialise le nb de pion
        self.__nbPionsJ1 = 0
        self.__nbPionsJ2 = 0
        # on lit les 10 lignes du plateau
        for i in range(0,10):
            line = plateauData[i]
            # on lit les 10 cases de la ligne
            for j in range(0,10):
                if line[j] not in ".\n":
                    # cette case contient un pion
                    if self.__cases[(i*10)+j].setPionSave(line[j]) == 1:
                        self.__nbPionsJ1 += 1
                    else:
                        self.__nbPionsJ2 += 1

    
    def getNbPions(self,joueur : int) -> int:
        if joueur == 1 :
            return self.__nbPionsJ1 
        elif joueur == 2 :
            return self.__nbPionsJ2
        else:
            print("ERREUR INTERNE dans getNbPions")

    def decrementePions(self,joueur : int, nbPions : int):
        if joueur == 1:
            self.__nbPionsJ1 -= nbPions
        elif joueur == 2:
            self.__nbPionsJ2 -= nbPions
        else:
            print("ERREUR INTERNE dans decrementePions")

    def affiche(self) -> str:
        txt = str()
        nbCases = 0
        txt += "```"
        txt += "  1 2 3 4 5 6 7 8 9 10\n"
        for case in self.__cases:
            nbCases+=1
            if ((nbCases-1)%10) == 0:
                txt += f"{self.__lignes[(int)(nbCases/10)]}"
            txt += f"{case.affiche()}"
            if (nbCases%10) == 0:
                txt += "\n"
        txt += self.affichePionsRestants()
        txt += "```"
        return txt
    
    def sauvegarde(self) -> str:
        lignes = ""
        nbCases = 0
        for case in self.__cases:
            nbCases+=1
            lignes += case.affiche(sauvegarde=True)
            if (nbCases%10) == 0:
                lignes += "\n"
        return lignes

        
    def affichePionsRestants(self) -> str:
        txt = str()
        pionAffiche = Pion(1)    
        txt += "\t"
        txt += f"{pionAffiche.affiche()}"
        txt += f" = {self.__nbPionsJ1}\n"
        txt += "\t"
        pionAffiche.setJoueur(2)
        txt += f"{pionAffiche.affiche()}"
        txt += f" = {self.__nbPionsJ2}\n"
        return txt

    def getCaseId(self,coords : str) -> int:
        if len(coords) < 2 or len(coords) > 3:
            return False
        # récupération de la ligne
        ligne = coords[0].upper()
        # récupération de la colonne
        col = coords[1:]
        if col[:-1] == "\n" :
            col.remove[:-1]
        try:
            col = int(col)  
        except:
            return False
        # vérification que c'est bien dans le tableau
        if ligne not in self.__lignes:
            # print(f"ligne {ligne} hors tableau")
            return False
        if col not in range(1,11):
            # print(f"colonne {col} hors tableau")
            return False        
        # on détermine l'id par le n° de col/ligne
        numLigne = self.__lignes.find(ligne)
        return ((numLigne*10) + (col-1))

        

    def getCase(self,coords : str) -> Case:
        return self.__cases[self.getCaseId(coords)]


    def pionAuJoueur(self,coords : str, joueur : int) -> bool:
        case = self.getCase(coords)
        if case != False :
            return case.estAuJoueur(joueur)
        return False

    def getCoordsCasesTraversees(self,case1 : Case, case2 : Case) -> list[str]:
        # on récupère la distance entre les 2 cases : et si elle est bien en diagonale
        indexV1 = case1.getPosY()
        indexV2 = case2.getPosY()
        indexH1 = self.__lignes.find(case1.getPosX())
        indexH2 = self.__lignes.find(case2.getPosX())
        nbCases = abs(indexV1 - indexV2)
        if abs(indexH1-indexH2) != nbCases:
            # print("Le déplacement n'est pas en diagonale")
            return []
        # on génère les coordonnées des cases à récup
        sensH = indexH2 > indexH1
        sensV = case2.getPosY() > case1.getPosY()
        coords = []
        for i in range(0,nbCases+1):
            coord = ""
            if sensH:
                coord = f"{self.__lignes[indexH1+i]}"
            else:
                coord = f"{self.__lignes[indexH1-i]}"
            if sensV:
                coord += f"{indexV1+i}"
            else:
                coord += f"{indexV1-i}"
            coords.append(coord)
        return coords

    def getIdCasesTraversees(self,case1 : Case, case2 : Case) -> list[int]:
        ids = []
        coords = self.getCoordsCasesTraversees(case1, case2)
        for coord in coords:
            ids.append(self.getCaseId(coord))
        return ids


    def getCasesTraversees(self,case1 : Case, case2 : Case) -> list[Case]:
        cases = []
        coords = self.getCoordsCasesTraversees(case1, case2)
        for coord in coords:
            cases.append(self.getCase(coord))
        return cases


    def deplacementValide(self,coords : list[str], joueur : int, pion : Pion = None) -> int:
        # vérification si la case existe et est vide
        cases = []
        for i in range(0,2):
            cases.append(self.getCase(coords[i]))
            if cases[i] == False :
                return 0 , "Case de destination non valide."
        if cases[1].estVide() == False:
            return 0 , "Case de destination non vide."
        # vérification de la distance
        cases = self.getCasesTraversees(cases[0],cases[1])

        if len(cases) <= 1:
            return 0 , "Case de destination non valide."

        # on vérifie s'il y a un pion à soi-même sur le chemin (sans compter la 1re et dernière case)
        for i in range(1,len(cases)-1):
            if not(cases[i].estVide()):
                # print(f"case {cases[i].getPosX()}{cases[i].getPosY()} pas vide")
                if cases[i].getPion().getJoueur() == joueur:
                    return 0 , "Un pion à soi-même est sur le chemin."

        # soit on assume que le pion est sur la case de départ
        # soit c'est un pion qui fait du miam multiple, et il n'est pas encore arrivé
        # sur la case de départ, alors il faut envoyer en paramètre de fonction
        if pion == None:
            pion = cases[0].getPion()
        # dame ou simple pion ?
        if pion.estDame() :
            for i in range(1,len(cases)-1):
                if not cases[1].estVide():
                    # pion du joueur adverse sur le chemin
                    return 2 , "Le joueur adverse va se faire manger !"
            # pas de pion du joueur adverse sur le chemin
            return 1 , f"Déplacement de {len(cases)-1} cases."
        else:
            if len(cases) > 3:
                return 0 , "Un pion ne peut pas se déplacer aussi loin !"
            elif (len(cases)) == 3:
                if not cases[1].estVide():
                    return 2 , "Le joueur adverse va se faire manger !"
                else:
                    return 0 , "Un pion peut se déplacer de 2 cases que s'il y a un pion adversaire entre les 2."
            elif len(cases) == 2:
                versLeHaut = cases[0].estPlusBas(cases[len(cases)-1])
                if (joueur == 1 and not versLeHaut) or ( joueur == 2 and versLeHaut):
                    return 0 , "Déplacement dans le sens contraire de la marche"
                else:
                    return 1 , "Déplacement d'une case."
        return 0 , "ERREUR INTERNE : deplacementValide() n'a pas déterminé la possibilité de se déplacer."

    def boutDuPlateau(self,joueur: int, caseId: int) -> bool:
        if joueur == 1:
            if self.__cases[caseId].getPosX() == 'A':
                return True
        if joueur == 2:
            if self.__cases[caseId].getPosX() == 'J':
                return True
        return 0

    def deplace_pion(self,coords : list[str], joueur : int) -> int:
        # on récupère les identifiants des cases, pour pouvoir les modifier ensuite
        case1 = self.getCase(coords[0])
        case2 = self.getCase(coords[1])
        ids = self.getIdCasesTraversees(case1,case2)
        # on supprime tous les pions sur le chemin (sans compter la case initiale et finale)
        pionsManges = 0
        for i in range(1,len(ids)-1):
            pionsManges += self.__cases[ids[i]].supprPion()
        # on déplace le pion à la zone d'arrivée
        pionCourant = self.__cases[ids[0]].recupPion()
        self.__cases[ids[-1]].setPion(pionCourant)

        # on le transforme en dame si nécessaire
        if not self.__cases[ids[-1]].getPion().estDame():
            if self.boutDuPlateau(joueur,ids[-1]):
                self.__cases[ids[-1]].getPion().setDame(True)

        return pionsManges
