from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from dateutil import tz as _tz
import datetime
import pytz
from datetime import datetime as _datetime
import os
import urllib2
import json


app = Flask(__name__)

def timeConvert(miliTime):
    """ convert millitary time to standard time.
    """
    hours, minutes, seconds = miliTime.split(":")
    hours, minutes, seconds = int(hours), int(minutes), int(seconds)
    setting = " PM"
    if hours > 12:
        setting = " AM"
        hours -= 12
    return "%02d:%02d:%02d"  % (hours, minutes, seconds) + setting

def get_weather(city, count=1):
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt={}&mode=json&units=metric&appid=c0d8761ca979157a45651a5c7f12a6be".format(city, count)
    response = urllib2.urlopen(url).read()
    return response


def getIP():
    """ get ip of visitor.
    """
    url = "http://ipinfo.io/ip"
    return urllib2.urlopen(url).read().strip()

def getLongLatFromIP(ip):
    city = getCityFromMyIp(ip)
    url = "http://maps.googleapis.com/maps/api/geocode/json?address={}&sensor=false".format(city)

    response = urllib2.urlopen(url)
    data = json.load(response)
    if data["status"] == u'OK':
        lat = data["results"][-1]["geometry"]["bounds"]["northeast"]["lat"]
        lng = data["results"][-1]["geometry"]["bounds"]["northeast"]["lng"]
        city = data["results"][-1][u"address_components"][0]["long_name"]
        return lat, lng, city
    return (None, None, None)


def getCityFromMyIp(ip):
    """  fetch city based on user local public ip
    """
    geoloc = "http://ip-api.com/json/{}".format(ip)
    data = json.load(urllib2.urlopen(geoloc))
    return str(data["city"])

def getSunriseSunset(lat, lng, date, timezone):
    """ provides sunrise and sunset time in 
        local timezone of city whose longitude 
        and latitude are given.

        Args:
            latitude (float): latitude location value
            longitude (float): longitudnal location value
            date (str): date for which sunrise and sunset
                is requested.
            timezone (str): timezone to convert utc tp local time

        Returns:
            (tuple): sunrise and sunset in standard time

    """
    # https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&date=2017-07-31
    url = "https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}".format(lat, lng, date)
    data = json.load(urllib2.urlopen(url))
    sunrise = data.get("results").get("sunrise").split()[0] # remove AM/PM from UTC time
    sunset =  data.get("results").get("sunset").split()[0]
    return convertUTCtoLocal(date, sunrise, timezone), convertUTCtoLocal(date, sunset, timezone)


def convertUTCtoLocal(date, utcTime, timezone):
    """ converts UTC time to given timezone
    """
    to_zone = pytz.timezone(timezone)
    from_zone = _tz.gettz('UTC')
    utc = _datetime.strptime('%s %s' % (date, utcTime), '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    return timeConvert(str(local.time()))


def getTimeZone(latitude, longitude):
    """ Provides timezone for a given longitude and latitude
    """
    # Note: We can also use this web service to get sunrise 
    # and sunset but due to inacuracy we use surise-sunset.org
    print "getting time zone from web service"
    url = "http://api.geonames.org/timezoneJSON?formatted=true&lat={}&lng={}&username=seaurchin".format(
        latitude,
        longitude)
    try:
        resp = urllib2.urlopen(url)
    except Exception:
        return (0, 0)
    geoData = json.load(resp)
    return geoData.get("timezoneId")

@app.route("/")
def index():
    searchCity = None
    lat = None
    lng = None
    count = None
    timeZone = None
    if request.method == "GET":
        searchCity = request.args.get("searchcity")
    else:
        searchCity = request.form.get("searchcity")

    if not searchCity:
        searchCity = request.cookies.get("last_search")

    if not searchCity:
            lat, lng, searchCity = getLongLatFromIP(getIP())

    count = request.args.get("count") or request.cookies.get("count", 1)


    try:
        weatherData = get_weather(searchCity, count=count)
    except Exception:
        return render_template("invalid_city.html", user_input=searchCity)
    data = json.loads(weatherData)
    try:
        city = data["city"]["name"]
    except KeyError:
        return render_template("invalid_city.html", user_input=searchCity)
    country = data["city"]["country"]

    lat = lat or data["city"]["coord"]["lat"]
    lng = lng or data["city"]["coord"]["lon"]
    forcast_list = []
    timeZoneCookeName = "{}_{}_{}".format(city.lower(), lat, lng)
    print "Retrieving %s cookie %s for city %s" % (timeZoneCookeName, request.cookies.get(timeZoneCookeName), city)
    timeZone = request.cookies.get(timeZoneCookeName)

    if not timeZone:
        timeZone = getTimeZone(lat, lng)

    for d in data.get("list"):
        date = _datetime.fromtimestamp(d.get('dt')).strftime('%Y-%m-%d')
        mini = d.get("temp").get("min")
        maxi = d.get("temp").get("max")
        humid = "N/A" if d.get("humidity") == 0 else d.get("humidity")
        desc = d.get("weather")[0].get("description")
        sunrise , sunset =  getSunriseSunset(lat, lng, date, timeZone)
        forcast_list.append((date, mini, maxi, humid, desc, sunrise, sunset))
    response = make_response(render_template("index.html", forcast_list=forcast_list, 
        lat=lat, lng=lng, city=city,country=country, count=count or request.cookies.get("count")))
    if request.args.get("remember"):
        response.set_cookie("last_search", "{},{}".format(city, country),
                expires=_datetime.today() + datetime.timedelta(days=365))
    response.set_cookie(timeZoneCookeName, timeZone,
            expires=_datetime.today() + datetime.timedelta(days=365))
    response.set_cookie("count", str(count),
            expires=_datetime.today() + datetime.timedelta(days=365))
    return response


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


