""" this module contains generic utility functions for the weather app.
"""

import json
import urllib2

def getJsonFromURL(url, timeout=15):
    try:
        response = urllib2.urlopen(url, timeout=timeout).read()
    except Exception:
        raise ValueError("Failed to load URL")
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

def getIP():
    """ get ip of visitor.
    """
    return urllib2.urlopen("http://ipinfo.io/ip").read().strip()
