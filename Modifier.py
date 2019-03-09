class Modifier(self):

    def __init__(self):
        self._incremental_objective = 0
        self._objective = 0
        self._original_objective = 0
        self._value = 0
        self._active = False

    def setObjective(self, obj):
        self._original_objective = obj

    def updateObjective(self, value):
        self._incremental_objective += value
        self._objective = self._original_objective + self._incremental_objective
        self._active = True
    
    def update(self, current_temp):
        if self._active:
            self._value = max([self._objective, current_temp]) - min([self._objective, current_temp])
            print("[Modifier][update] Valeur du modifier : ", self._value) # @debug
            if self._value < 0:
                self._active = False
                self._incremental_objective = 0

    def getValue(self):
        val = 0
        if self._active:
            val = self._value
        return val