import datetime
import json

class Thermostat():
    def __init__(self):
        self.on = True
        self.goal = 22.0
        self.temperature = 21.5

    def setTemperature(self, temp):
        self.goal = temp

    def getCurrentTemperature(self):
        return self.temperature

    def setWorking(self, working):
        self.on = working

    #TODO: behave depending on rules.json
    def getRequireTemp(self, hour):
        now = datetime.datetime.now()
        day = "lundi" #now.day
        hour = hour #now.hour
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
        #print("Heure : ", argHour, ", Temperature : ", tempToSet)
        return tempToSet
