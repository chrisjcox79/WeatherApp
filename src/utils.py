""" this module contains generic utility functions for the weather app.
"""

import json
import urllib2
import string
import random
from flask import request

cityNameMap = {
    "Bengaluru" : "Bangalore",

}


def getClientIp():
    """ helper function to mock request module.
    """
    return request.access_route[0]

def getCityFromMyIp(ip):
    """ fetch city based on user local public ip
    """
    ip = ip if ip != "127.0.0.1" else ""
    geoloc = "http://ip-api.com/json/{}".format(ip)
    data = json.load(urllib2.urlopen(geoloc))
    return cityNameMap.get(data.get("city"), data.get("city"))


def getLongLatFromIP(ip):
    city = getCityFromMyIp(ip)
    if city:
        url = "http://maps.googleapis.com/maps/api/geocode/json?address={}&sensor=false".format(city)
        response = urllib2.urlopen(url)
        data = json.load(response)
        if data["status"] == u'OK':
            lat = data["results"][-1]["geometry"]["bounds"]["northeast"]["lat"]
            lng = data["results"][-1]["geometry"]["bounds"]["northeast"]["lng"]
            city = data["results"][-1][u"address_components"][0]["long_name"]
            return lat, lng, city
    return ("31.03", "75.79", "Phillaur")


def getplace(lat, lon):
    """ get the place from latitude and longitude.
    """
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng={},{}&sensor=false".format(lat, lon)
    j = getJsonFromURL(url)
    town = country = None
    if j["status"] != "fail":
        components = j['results'][0]['address_components']
        for c in components:
            if "political" in c['types'] and "locality" in c['types']:
                town = c['long_name']
            if "country" in c['types']:
                country = c['long_name']
    return town, country


def getJsonFromURL(url, timeout=5):
    """ opens provided url and provides json data
    """

    try:
        response = urllib2.urlopen(url, timeout=timeout).read()
    except Exception, er:
        return {"status": "fail", "Description": "this is manually forced due to {}".format(er.message)}
    try:
        data = json.loads(response)
    except ValueError:
        return {"status": "fail" }
    return json.loads(response)


def getCityDateTime(timezone):
    url = "https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz={}".format(timezone)
    data = getJsonFromURL(url)
    if data.get("status"):
        return (
            "{}:{}:{}".format(data.get("hours"), data.get("minutes"), data.get("seconds")),
            "{}/{}".format(data.get("day"), data.get("monthName"))
                )

def getVisitorAddressFromLatLong(lat, lng):
    """ provides address based on latitude and longitude
    """
    return getJsonFromURL("http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}".format(lat, lng))

def getWeatherURL(city, count=2):
	return "http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt={}&mode=json&units=metric&appid=c0d8761ca979157a45651a5c7f12a6be".format(city, count)

# http://weathers.co/api.php?city=Bangalore # try this for weather table header

def getSunriseSunsetURL(lat, lng, date):
	return "https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}".format(lat, lng, date)

def getTimeZoneURL(latitude, longitude):
	return "http://api.geonames.org/timezoneJSON?formatted=true&lat={}&lng={}&username=seaurchin".format(
        latitude,
        longitude)

def id_generator(size=9, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def getTimezoneFromIP(ip):
    ip = ip if ip != "127.0.0.1" else ""
    data = getJsonFromURL("http://ip-api.com/json/{}".format(ip))
    tz = "Asia/Kolkata" if ip == "127.0.0.1" else "UTC"
    if data["status"] == "success":
        tz = data["timezone"]
    return tz

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
