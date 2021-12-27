#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
from aperoV2_files.moment_class import Moment


class Apero:
    """classe apéro"""

    def __init__(self):
        """initialisation :"""

        """champs"""
        self.__hebergeur = None
        self.__moment = Moment()
        self.__description = None

    """setters et getters"""
    """
        servent à enregistrer les champs (variables de la classe)
        et à les obtenir si on le souhaite.
    """

    def setHebergeur(self, nom_hebergeur: str):
        self.__hebergeur = nom_hebergeur

    def getHebergeur(self) -> str:
        return self.__hebergeur

    def setMoment(self, type: str, value: str):
        self.__moment.setMoment(type, value)

    def getMoment(self) -> datetime :
        return self.__moment.getDateTime()

    def getFin(self) -> datetime :
        return self.__moment.getDateTimeFin()


    def getDescription(self) -> str:
        return self.__description

    def setDescription(self, description: str):
        self.__description = description


    """afficher les données comme passées dans le message"""

    def affiche_brut(self):
        print(f"Hébergeur : \"{self.__hebergeur}\"")
        self.__moment.affiche_brut()
        print(f"description : \"{self.__description}\"")
        self.__moment.affiche()
