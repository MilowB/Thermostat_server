import datetime
import locale
import time
import json
import urllib.request

# Thermostat is the temperature regulator interacting with the API
class Thermostat():

    def __init__(self):
        ## public attribute ##
        self.heating = False
        ## private attributes ##
        self._on = True
        self._upper = False
        self._goal = 22.0
        self._temperature = 21.5
        self._required_temp = 21.5
        self._required_temp_modifier = 0
        self._curr_required_temp_modifier = 0
        self._csv_data = []

    ########################## PUBLIC METHODS ##########################

    def set_temperature(self, temp):
        self._goal = temp

    def getCurrent_temperature(self):
        return self._temperature

    def setWorking(self, working):
        self._on = working

    def getWorking(self):
        return self._on

    def setRequired_temp_modifier(self, value):
        self._required_temp_modifier += value
        if self._curr_required_temp_modifier == 0:
            self._curr_required_temp_modifier = self._required_temp_modifier

    def getCurr_required_temp_modifier(self):
        return self._curr_required_temp_modifier

    def needHeating(self):
        res = False
        if self._on:
            temp_required = self._getRequiredTemp()
            if self._temperature > temp_required:
                self._upper = True
            if self._temperature < temp_required and not self._upper:
                res = True
            elif self._temperature >= temp_required - 0.5 and self._temperature < temp_required and self._upper:
                res = False
            elif self._temperature < temp_required - 0.5:
                res = True
                self._upper = False
        return res

    def updateData(self):
        contenuFich = self._lireFichier("/sys/bus/w1/devices/28-04178033e5ff/w1_slave")
        _temperature = self._recupTemp(contenuFich)
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
        contents = urllib.request.urlopen(address).read()
        my_json = contents.decode('utf8').replace("'", '"')
        # Load the JSON to a Python list & dump it back out as formatted JSON
        data = json.loads(my_json)
        s = json.dumps(data, indent=4, sort_keys=True)
        return data["main"]["temp"] - 273.15
            
    ########################## PRIVATE METHODS ##########################

    def _getRequiredTemp(self):
        locale.setlocale(locale.LC_TIME,'')
        day = time.strftime('%A')
        hour = self._getHour()
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
        # Si une nouvelle règle de température apparait, le modificateur de temp doit être réinitialisé
        if tempToSet != self._required_temp:
            self._required_temp_modifier = 0
            self._curr_required_temp_modifier = 0
        self._required_temp = tempToSet
        self._curr_required_temp_modifier = (tempToSet + self._required_temp_modifier) - self._temperature
        if abs(self._curr_required_temp_modifier) > abs(self._required_temp_modifier):
            self._curr_required_temp_modifier = self._required_temp_modifier
        return tempToSet + self._curr_required_temp_modifier

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