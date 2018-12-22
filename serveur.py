from flask import Flask, jsonify
from flask import abort
from flask_httpauth import HTTPBasicAuth
from flask import request
import sys
import json

sys.path.insert(0, '/home/mickael/Projets/Thermostat/Intelligence/')

from Thermostat import *
from Simulateur import *
auth = HTTPBasicAuth()

app = Flask(__name__)
thermostat = Thermostat()

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
    return jsonify('{"status": "success", "temperature":' + str(thermostat.getCurrentTemperature()) + '}')

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
    thermostat.setTemperature(request.json["temperature"])
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
    thermostat.setWorking(request.json["working"])
    return jsonify('{"status": "success"}')

def auth(key):
    file = open("config.txt", "r") 
    if file.read() == key:
        return True
    return False