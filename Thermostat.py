import datetime
import locale
import time
import json
import urllib.request
import logging
from Modifier import *

# Thermostat is the temperature regulator class interacting with the API
class Thermostat():

    def __init__(self):
        logging.basicConfig(filename='thermostat.log',level=logging.DEBUG)
        ## public attribute ##
        self.heating = False
        ## private attributes ##
        self._on = True
        self._upper = False
        self._goal = 22.0
        self._temperature = 21.5
        self._required_temp = 21.5
        self._exterior_temp = 0
        self._modifier = Modifier()
        self._csv_data = []
        self._x = 6.40
        self._y = 6.40
        self._z = 2.50
        self._volume = self._x * self._y * self._z
        self._masse_vol_air = 1.225
        self._masse_air = self._volume * self.masse_vol_air
        self._capacite_cal_air = 1004
        #En Watt
        self.watt_chauffage = 1500
        self.perte_isolation = 1100

    ########################## PUBLIC METHODS ##########################

    def set_temperature(self, temp):
        self._goal = temp

    def getCurrent_temperature(self):
        return self._temperature

    def setWorking(self, working):
        self._on = working

    def getWorking(self):
        return self._on

    def getRequiredTemp(self):
        return self._required_temp

    def setRequired_temp_modifier(self, value):
        self._modifier.updateObjective(value, self._temperature)
        self._modifier.update(self._getTemperature())

    def getCurr_required_temp_modifier(self):
        self._modifier.update(self._getTemperature())
        return self._modifier.getValue()

    def needHeating(self):
        res = False
        if self._on:
            temp_required = self._getRequiredTemp()
            if self._temperature > temp_required:
                self._upper = True
            if self._temperature < temp_required or self._anticipateHeating() and not self._upper:
                res = True
            elif self._temperature >= temp_required - 0.5 and self._temperature < temp_required and self._upper:
                res = False
            elif self._temperature < temp_required - 0.5:
                res = True
                self._upper = False
        return res

    def updateData(self):
        _temperature = self._getTemperature()
        # Update _temperature
        self._temperature = _temperature
        # Update data to write into the CSV  
        exterior_temp = self.getExteriorTemp()
        self._csv_data.append([self._getHour(), self._temperature, exterior_temp, self.heating])

    def saveData(self):
        # Save data for history
        with open('history.csv', 'a') as outfile:
            for csv in self._csv_data:
                outfile.write(str(csv[0]) + " " + str(csv[1]) + " " + str(csv[2]) + " " + str(csv[3]) + "\n")
        self._csv_data = []

    def getExteriorTemp(self):
        # Coordinates of Valence, FR
        long = 4.89
        lat = 44.93
        # Get the API key from the config file
        with open("config.txt") as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        api_key = content[1].split(" ")[1]
        address = "http://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(long) + "&appid=" + api_key
        contents = None
        try:
            contents = urllib.request.urlopen(address).read()
        except:
            print("[Thermostat][getExteriorTemp] Erreur : Le endpoint openweathermap ne repond pas !") #@debug
        if contents != None:
            my_json = contents.decode('utf8').replace("'", '"')
            # Load the JSON to a Python list & dump it back out as formatted JSON
            data = json.loads(my_json)
            #s = json.dumps(data, indent=4, sort_keys=True) # to see if it's really useless or not (I bet it is)
            self._exterior_temp = data["main"]["temp"] - 273.15
            return data["main"]["temp"] - 273.15
        self._exterior_temp = contents
        return contents

    ########################## PRIVATE METHODS ##########################

    # Time in minute to heat the appartment
    def _timeNeededToHeat(self, required):
        ext = self._exterior_temp
        inte = self._getTemperature()
        self.perte_isolation += 15 * (inte - ext)
        # Energy in Kj, 1 kj = 0.277778 Wh
        energy = self.masse_air * self.capacite_cal_air * (required - inte)
        # Time in seconde
        time = energy / (self.heating - self.perte_isolation)
        return time / 60

    def _anticipateHeating(self):
        heat = False
        #read rules
        day = time.strftime('%A')
        hour = self._getHour()
        try:
            with open('rules.json', 'r') as outfile:
                jsonread = json.load(outfile)
                if day in jsonread:
                    rule = jsonread[day]["data"]
                    #read hour
                    for r in rule:
                        if hour <= r["hour"]:
                            tempToSet = r["temperature"]
                            time_to_heat = self._timeNeededToHeat(tempToSet)
                            # Convert it in hour (e.g. 100mn = 1.40h)
                            time_to_heat = (time_to_heat % 60) / 100 + int(time_to_heat / 60)
                            time_soustracted = hour_soustraction(r["hour"], time_to_heat)
                            if time_soustracted <= float(hour):
                                heat = True
                else:
                    logging.warning('[_getRequiredTemp()] Erreur, jour introuvable')
        except:
            logging.warning('[_getRequiredTemp()] Erreur de lecture de rules.json')
        return heat

    def _hour_soustraction(self, h1, h2):
        t = float(h1) - float(h2)
        t -= int(t)
        reste = 1 - t
        completude = 0.60 - reste
        return int(float(h1) - float(h2)) + completude

    def _getRequiredTemp(self):
        locale.setlocale(locale.LC_TIME,'')
        day = time.strftime('%A')
        hour = self._getHour()
        tempToSet = -1
        #read rules
        try:
            with open('rules.json', 'r') as outfile:
                jsonread = json.load(outfile)
                if day in jsonread:
                    rule = jsonread[day]["data"]
                    #read hour
                    for r in rule:
                        if hour >= r["hour"]:
                            tempToSet = r["temperature"]
                        else:
                            break
                else:
                    logging.warning('[_getRequiredTemp()] Erreur, jour introuvable')
        except:
            logging.warning('[_getRequiredTemp()] Erreur de lecture de rules.json')
        # Si une nouvelle règle de température apparait, le modificateur de temp doit être réinitialisé
        if tempToSet != self._required_temp:
            self._required_temp_modifier = 0
            self._curr_required_temp_modifier = 0
        self._required_temp = tempToSet
        self._modifier.setObjective(tempToSet)
        self._modifier.update(self._getTemperature())
        return tempToSet + self._modifier.getValue()

    def _lireFichier(self, emplacement) :
        # Ouverture du fichier contenant la _temperature
        fichTemp = open(emplacement)
        # Lecture du fichier
        contenu = fichTemp.read()
        # Fermeture du fichier apres qu'il ai ete lu
        fichTemp.close()
        return contenu

    def _recupTemp(self, contenuFich) :
        # Supprimer la premiere ligne qui est inutile
        secondeLigne = contenuFich.split("\n")[1]
        _temperatureData = secondeLigne.split(" ")[9]
        # Supprimer le "t="
        _temperature = float(_temperatureData[2:])
        # Mettre un chiffre apres la virgule
        _temperature = _temperature / 1000
        return _temperature

    def _getHour(self):
        hour = time.strftime('%H')
        minute = time.strftime('%M')
        hour = int(hour) + int(minute) / 100
        return hour

    def _getTemperature(self):
        contenuFich = self._lireFichier("/sys/bus/w1/devices/28-04178033e5ff/w1_slave")
        return self._recupTemp(contenuFich)