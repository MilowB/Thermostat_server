import datetime
import locale
import time
import json

class Thermostat():
    def __init__(self):
        self.on = True
        self.upper = False
        self.goal = 22.0
        self.temperature = 21.5

    def setTemperature(self, temp):
        self.goal = temp

    def getCurrentTemperature(self):
        return self.temperature

    def setWorking(self, working):
        self.on = working

    #TODO: behave depending on rules.json
    def _getRequireTemp(self):
        locale.setlocale(locale.LC_TIME,'')
        day = time.strftime('%A')
        hour = time.strftime('%H')
        minute = time.strftime('%M')
        hour = int(hour) + int(minute) / 100
        tempToSet = 0
        #read rules
        with open('rules.json', 'r') as outfile:
            jsonread = json.load(outfile)
            argHour = 0
            if day in jsonread:
                rule = jsonread[day]["data"]
                #read hour
                for r in rule:
                    if hour >= r["hour"]:
                        tempToSet = r["temperature"]
                        argHour = r["hour"]
                    else:
                        break
            else:
                print("[Thermostat][behave] Error, day not found")
        return tempToSet

    def needHeating(self):
        res = False
        temp_required = self._getRequireTemp()
        if self.temperature > temp_required:
            self.upper = True
        if self.temperature < temp_required and not self.upper:
            res = True
        elif self.temperature >= temp_required - 0.5 and self.temperature < temp_required and self.upper:
            res = False
        elif self.temperature < temp_required - 0.5:
            res = True
            self.upper = False
        return res

    def updateData(self):
        contenuFich = self._lireFichier("/sys/bus/w1/devices/28-04178033e5ff/w1_slave")
        temperature = self._recupTemp(contenuFich)
        self.temperature = temperature

    def _lireFichier(self, emplacement) :
        # Ouverture du fichier contenant la temperature
        fichTemp = open(emplacement)
        # Lecture du fichier
        contenu = fichTemp.read()
        # Fermeture du fichier apres qu'il ai ete lu
        fichTemp.close()
        return contenu

    def _recupTemp(self, contenuFich) :
        # Supprimer la premiere ligne qui est inutile
        secondeLigne = contenuFich.split("\n")[1]
        temperatureData = secondeLigne.split(" ")[9]
        # Supprimer le "t="
        temperature = float(temperatureData[2:])
        # Mettre un chiffre apres la virgule
        temperature = temperature / 1000
        return temperature

