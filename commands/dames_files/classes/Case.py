from classes.Pion import Pion

class Case:
    """classe Case"""

    def __init__(self,posX : str,posY : int, claire : bool):
        """initialisations :"""
        
        self.__posX = posX
        self.__posY = posY
        self.__pion = None
        self.__claire = claire
        
        self.__CaseClaireAff = "🟧"
        self.__CaseFonceeAff = "🟫"
        self.__CaseFic = "."

        
    def estVide(self) -> bool:
        if self.__pion != None:
            return False
        return True

    def estAuJoueur(self,joueur :int) -> bool:
        if self.__pion != None:
            if self.__pion.getJoueur() == joueur:
                return True
        return False

    def estClaire(self) -> bool:
        return self.__claire

    def supprPion(self) -> int:
        # on supprime le pion de la variable,
        # et on renvoie le nb de pions supprimés
        if self.__pion != None:
            self.__pion = None
            return 1
        return 0


    def recupPion(self) -> Pion:
        pion = self.__pion
        self.supprPion()
        return pion
        
    def setPion(self, pion : Pion):
        self.__pion = pion

    def setPionSave(self, pionSave : str) -> int:
        pion = Pion()
        if pionSave.lower() == pion.getValSave(1):
            pion.setJoueur(1)
        elif pionSave.lower() == pion.getValSave(2):
            pion.setJoueur(2)
        else:
            print("ERREUR DE FICHIER dans Case.py/setPionSave()")
            print(f"\tLe fichier de sauvegarde contient le caractère \"{pionSave}\" non reconnu.")
        dames = f"{pion.getValSave(1,True)}{pion.getValSave(2,True)}"
        if pionSave in dames:
            pion.setDame(True)
        self.__pion = pion
        return self.__pion.getJoueur()

    def getPion(self) -> Pion:
        if self.__pion == None:
            return False
        return self.__pion

    def getPosX(self) -> str:
        return self.__posX

    def getPosY(self) -> int:
        return self.__posY

    def estPlusBas(self,case2) -> bool :
        if  self.getPosX() < case2.getPosX() :
            return False
        return True

    def affiche(self,sauvegarde=False) -> str:
        if self.__pion == None:
            if sauvegarde:
                return self.__CaseFic
            else:
                if self.__claire :
                    return self.__CaseClaireAff
                else:
                    return self.__CaseFonceeAff
        else:
            if sauvegarde:
                return self.__pion.affiche(sauvegarde=True)
            else:
                return self.__pion.affiche()