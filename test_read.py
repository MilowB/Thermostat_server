import urllib.request
import json

# Coordinates of Valence, FR
long = 4.89
lat = 44.93
# Get the API key from the config file
with open("config.txt") as f:
    content = f.readlines()
content = [x.strip() for x in content] 
api_key = content[1].split(" ")[1]
address = "https://samples.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(long) + "&appid=" + api_key
print(address)
contents = urllib.request.urlopen(address).read()
my_json = contents.decode('utf8').replace("'", '"')
# Load the JSON to a Python list & dump it back out as formatted JSON
data = json.loads(my_json)
s = json.dumps(data, indent=4, sort_keys=True)
print(data["main"]["temp"] - 273.15)
