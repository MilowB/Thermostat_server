class Modifier():

    def __init__(self):
        self._incremental_objective = 0
        self._objective = 0
        self._original_objective = 0
        self._original_temp = 0
        self._value = 0
        self._active = False

    def setObjective(self, obj):
        self._original_objective = obj

    def updateObjective(self, value, original_temp):
        self._incremental_objective += value
        self._objective = self._original_objective + self._incremental_objective
        self._original_temp = original_temp
        self._active = True
    
    def update(self, current_temp):
        if self._active:
            self._value = self._objective - current_temp
            print("[Modifier][update] Valeur du modifier : ", self._value) # @debug
            if self._objective > self._original_temp and self._value < 0:
                self._active = False
                self._incremental_objective = 0
            elif self._objective < self._original_temp and self._value > 0:
                self._active = False
                self._incremental_objective = 0

    def getValue(self):
        val = 0
        if self._active:
            val = self._value
        return val