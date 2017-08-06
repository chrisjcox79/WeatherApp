""" this module contains generic utility functions for the weather app.
"""

import json
import urllib2

def getJsonFromURL(url, timeout=5):
    try:
        response = urllib2.urlopen(url, timeout=timeout).read()
    except Exception:
        raise ValueError("Failed to load URL")
    return json.loads(response)

def getWeatherURL(city, count=2):
	return "http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt={}&mode=json&units=metric&appid=c0d8761ca979157a45651a5c7f12a6be".format(city, count)
