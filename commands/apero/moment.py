#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dateparser
import datetime

class Moment:
    """classe Moment"""

    def __init__(self):
        """initialisation :"""

        """champs"""
        self.__date_ecrite = None
        self.__j_semaine = None
        self.__heure_ecrite = None
        self.__time = None
        self.__datetime = None
        self.__datetimeFin = None

        """constants"""
        self.__now = datetime.datetime.now()
        self.__HEURE_APERO = 19
        self.__MINUTE_APERO = 0

    """ setters """

    """Enregistrement d'une date écrite """

    def setDate(self, value: str):
        self.__date_ecrite = value
        # formule magique qui sort un objet datetime python
        # à partir de la date écrite (même en français)
        self.__datetime = dateparser.parse(self.__date_ecrite,  settings={
                                           'TIMEZONE': 'Europe/Paris'})

        # si la formule magique place automatiquement la date dans le passé
        if self.__datetime < self.__now:
            # si on lance un apéro à un mois
            # d'un année suivante (sans préciser l'année)
            if self.__datetime.month < self.__now.month:
                self.__datetime = self.__datetime.replace(
                    year=self.__datetime.year + 1)
            # si on lance un apéro sans préciser le mois et que ça le place
            # automatiquement dans le passé
            elif self.__datetime.month == self.__now.month:
                month = self.__datetime.month
                if month == 12:
                    self.__datetime = self.__datetime.replace(
                        year=self.__datetime.year + 1, month=1)
                else:
                    self.__datetime = self.__datetime.replace(
                        month=self.__datetime.month + 1)
        self.majDateTime()

    """ Enregistrement d'une date selon le jour de la semaine """

    def setJSemaine(self, value: str):
        self.__j_semaine = value
        # la date passée explicitement a priorité sur le jour de la semaine
        if not self.__datetime:
            self.__datetime = dateparser.parse(self.__j_semaine, settings={
                                               'TIMEZONE': 'Europe/Paris'})
            # si on lance un apéro mardi pro à part qu'on est jeudi :
            # faut rajouter une semaine (sinon la date se met à mardi dernier)
            if self.__datetime < self.__now:
                self.__datetime = self.__datetime + datetime.timedelta(days=7)
        self.majDateTime()

    """ Enregsitrement de l'heure """

    def setHeure(self, value: str):
        self.__heure_ecrite = value
        self.__time = dateparser.parse(self.__heure_ecrite, settings={
                                       'TIMEZONE': 'Europe/Paris'})
        self.majDateTime()

    """ Dispatcheur de l'information de date / heure reçue """

    def setMoment(self, type: str, value: str):
        print(f"set Moment de type \"{type}\" = \"{value}\"")
        if type == "date":
            self.setDate(value)
        elif type == "j_semaine":
            self.setJSemaine(value)
        elif type == "heure":
            self.setHeure(value)
        else:
            raise ValueError(
                f" type {type} non reconnu. Il doit valoir \"date\",\"j_semaine\" ou \"heure\"")

    """ Enregistrement final de la date après avoir les infos : on cumule les infos """

    def majDateTime(self):
        if not self.__datetime:
            self.__datetime = self.__now
        if self.__time:
            self.__datetime = self.__datetime.replace(
                hour=self.__time.hour, minute=self.__time.minute)
        else:
            self.__datetime = self.__datetime.replace(
                hour=self.__HEURE_APERO, minute=self.__MINUTE_APERO)

        self.__datetimeFin = self.__datetime.replace(
            hour=1, minute=0) + datetime.timedelta(days=1)

    """ getters """

    def getDateTime(self) -> datetime:
        return self.__datetime

    def getDateTimeFin(self) -> datetime:
        return self.__datetimeFin

    """ afficheurs dans la console """

    def affiche_brut(self):
        print(f"j_semaine : \"{self.__j_semaine}\"")
        print(f"date écrite : \"{self.__date_ecrite}\"")
        print(f"heure : \"{self.__heure_ecrite}\"")

    def affiche(self):
        print(self.__datetime.strftime("Moment : %A %d %B %Y à %Hh%M"))
