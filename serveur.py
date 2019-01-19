from flask import Flask, jsonify
from flask import abort
from flask_httpauth import HTTPBasicAuth
from flask import request
import json

auth = HTTPBasicAuth()

app = Flask(__name__)
thermostat = Thermostat()

#TODO mutex pour rules.json

@app.route("/")
def serveur():
    return "Server On !"

@app.route("/testPing", methods=['GET'])
def ping():
    return jsonify('{"status": "success"}')

@app.route("/data/temperature/<string:key>", methods=['GET'])
def getCurrentTemperature(key):
    if not auth(key):
        abort(401)
    contenuFich = lireFichier("/sys/bus/w1/devices/28-04178033e5ff/w1_slave")
    temperature = recupTemp (contenuFich)
    return jsonify('{"status": "success", "temperature":' + str(temperature) + '}')

@app.route("/data/planning/<string:key>", methods=['GET'])
def getPlanning(key):
    if not auth(key):
        abort(401)
    with open('rules.json', 'r') as outfile:
        jsonread = json.load(outfile)
        arr = str(jsonread).split("\"")
        tostring = ""
        for a in arr:
            tostring += "\"" + a
        tostring += "\""
        return jsonify('{"status": "success", "data": ' + tostring + '}')
    return jsonify('{"status": "error", "description": "Unable to get rules"}')

@app.route("/data/history/<string:key>", methods=['GET'])
def getHistory(key):
    if not auth(key):
        abort(401)
    return jsonify({'id': 0})

@app.route("/state/thermostat/<string:key>", methods=['GET'])
def getWorking(key):
    if not auth(key):
        abort(401)
    return jsonify('{"status": "success", "working": "true"}')

'''
key : authentification key to access the API
PUT - rules : json rules
'''
@app.route("/manage/planning/<string:key>", methods=['PUT'])
def setTemperatureRules(key):
    if not auth(key):
        abort(401)
    elif not "rules" in request.json:
        return jsonify('{"status": "error", "description": "Field "rules" missing"}')
    with open('rules.json', 'w') as outfile:
        json.dump(request.json["rules"], outfile)
    return jsonify('{"status": "success"}')

'''
key : authentification key to access the API
PUT - temperature : temperature to set
'''
@app.route("/manage/currentTemperature/<string:key>", methods=['PUT'])
def setCurrentTemperature(key):
    if not auth(key):
        abort(401)
    elif not "temperature" in request.json:
        return jsonify('{"status": "error", "description": "Field "temperature" missing"}')
    #TODO
    return jsonify('{"status": "success"}')

'''
key : authentification key to access the API
PUT - working : activate or desactivate the thermostat
'''
@app.route("/manage/thermostat/<string:key>", methods=['PUT'])
def setWorking(key):
    if not auth(key):
        abort(401)
    elif not "working" in request.json:
        return jsonify('{"status": "error", "description": "Field "working" missing"}')
    #TODO On/Off thermostat
    return jsonify('{"status": "success"}')

def auth(key):
    with open("config.txt") as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content] 
    if content[0].split(" ")[1] == key:
        return True
    return False

def lireFichier (emplacement) :
    # Ouverture du fichier contenant la temperature
    fichTemp = open(emplacement)
    # Lecture du fichier
    contenu = fichTemp.read()
    # Fermeture du fichier apres qu'il ai ete lu
    fichTemp.close()
    return contenu

def recupTemp (contenuFich) :
    # Supprimer la premiere ligne qui est inutile
    secondeLigne = contenuFich.split("\n")[1]
    temperatureData = secondeLigne.split(" ")[9]
    # Supprimer le "t="
    temperature = float(temperatureData[2:])
    # Mettre un chiffre apres la virgule
    temperature = temperature / 1000
    return temperature

if __name__ == '__main__':
   app.run(host="0.0.0.0")