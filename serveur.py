from flask import Flask, jsonify
from flask import abort
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = Flask(__name__)

@app.route("/")
def serveur():
    return "Hello World!"

@app.route("/data/temperature/<string:key>/<string:phrase>", methods=['GET'])
def getTemperature(key, phrase):
    if not auth(key):
        abort(401)
    return jsonify({'id': phrase})

@app.route("/data/history/<string:key>", methods=['GET'])
def getHistory(key):
    if not auth(key):
        abort(401)
    return jsonify({'id': 0})

def auth(key):
    file = open("config.txt", "r") 
    if file.read() == key:
        return True
    return False