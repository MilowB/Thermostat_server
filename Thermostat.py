import datetime
import locale
import time
import json
import urllib.request

class Thermostat():
    def __init__(self):
        self.on = True
        self.upper = False
        self.goal = 22.0
        self.temperature = 21.5
        self.csv_data = []

    def setTemperature(self, temp):
        self.goal = temp

    def getCurrentTemperature(self):
        return self.temperature

    def setWorking(self, working):
        self.on = working

    def getWorking(self):
        return self.on

    #TODO: behave depending on rules.json
    def _getRequireTemp(self):
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
        print(tempToSet, "a l'heure : ", argHour, " au jour : ", day)
        return tempToSet

    def needHeating(self):
        res = False
        print("[needHeating] self.on: ", self.on) #debug
        if self.on:
            temp_required = self._getRequireTemp()
            print("[needHeating] temp_required : ", temp_required) #debug
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
        # Update temperature
        self.temperature = temperature
        # Update data to write into the CSV  
        exterior_temp = self._getExteriorTemp()
        self.csv_data.append([self._getHour(), self.temperature, exterior_temp])

    def saveData(self):
        # Save data for history
        with open('history.csv', 'a') as outfile:
            for csv in self.csv_data:
                outfile.write(str(csv[0]) + " " + str(csv[1]) + " " + str(csv[2]) + "\n")
            

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

    def _getHour(self):
        hour = time.strftime('%H')
        minute = time.strftime('%M')
        hour = int(hour) + int(minute) / 100
        return hour

    def _getExteriorTemp(self):
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



