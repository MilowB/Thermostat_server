class Thermostat():
    def __init__(self):
        self.goal = 22.0
        self.temperature = 21.5

    def _setTemperature(self, temp):
        self.goal = temp

    def getCurrentTemperature(self):
        return self.temperature

    #TODO: behave depending on rules.json
    def behave(self):
        #read rules
        #read hour
        #find the temperature to set
        self._setTemperature(22.0)
        print("[Behave]")
