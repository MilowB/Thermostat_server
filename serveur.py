from flask import Flask, jsonify
from flask import abort
from flask_httpauth import HTTPBasicAuth
from flask import request
auth = HTTPBasicAuth()

app = Flask(__name__)

@app.route("/")
def serveur():
    return "Hello World!"

@app.route("/data/temperature/<string:key>", methods=['GET'])
def getTemperature(key):
    if not auth(key):
        abort(401)
    return jsonify({'temperature': 22.5})

@app.route("/data/planning/<string:key>", methods=['GET'])
def getPlanning(key):
    if not auth(key):
        abort(401)
    return jsonify({'id': 0})

@app.route("/data/history/<string:key>", methods=['GET'])
def getHistory(key):
    if not auth(key):
        abort(401)
    return jsonify({'id': 0})

'''
key : authentification key to access the API
PUT - rules : json rules
'''
@app.route("/manage/planning/<string:key>", methods=['PUT'])
def setTemperatureRules(key):
    if not auth(key):
        abort(401)
    elif not "rules" in request.json:
        abort(400)
    return jsonify(request.json)

'''
key : authentification key to access the API
PUT - temperature : temperature to set
'''
@app.route("/manage/currentTemperature/<string:key>", methods=['PUT'])
def setCurrentTemperature(key):
    if not auth(key):
        abort(401)
    elif not "temperature" in request.json:
        abort(400)
    return jsonify(request.json)

'''
key : authentification key to access the API
PUT - working : activate or desactivate the thermostat
'''
@app.route("/manage/thermostat/<string:key>", methods=['PUT'])
def setWorking(key):
    if not auth(key):
        abort(401)
    elif not "working" in request.json:
        abort(400)
    return jsonify(request.json)

def auth(key):
    file = open("config.txt", "r") 
    if file.read() == key:
        return True
    return False