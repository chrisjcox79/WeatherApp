""" this module contains generic utility functions for the weather app.
"""

import json
import urllib2
import string
import random
from flask import jsonify

def getJsonFromURL(url, timeout=15):
    try:
        response = urllib2.urlopen(url, timeout=timeout).read()
    except Exception:
        # raise ValueError("Failed to load URL")
        return {"status": "fail"}
    return json.loads(response)

def getWeatherURL(city, count=2):
	return "http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt={}&mode=json&units=metric&appid=c0d8761ca979157a45651a5c7f12a6be".format(city, count)

def getLongLatURL():
	pass

def getSunriseSunsetURL(lat, lng, date):
	return "https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}".format(lat, lng, date)

def getTimeZoneURL(latitude, longitude):
	return "http://api.geonames.org/timezoneJSON?formatted=true&lat={}&lng={}&username=seaurchin".format(
        latitude,
        longitude)

def id_generator(size=9, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def getHostIp():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
    except Exception:
        print("Network not reachable. defaulting to Home")
        return "127.0.0.1"
    ip = s.getsockname()[0]
    s.close()
    return ip
