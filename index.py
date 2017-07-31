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
import time

app = Flask(__name__)

def timeConvert(miliTime):
    hours, minutes, seconds = miliTime.split(":")
    hours, minutes, seconds = int(hours), int(minutes), int(seconds)
    setting = " PM"
    if hours > 12:
        setting = " AM"
        hours -= 12
    return "%02d:%02d:%02d"  % (hours, minutes, seconds) + setting

def get_weather(city):
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt=10&mode=json&units=metric&appid=c0d8761ca979157a45651a5c7f12a6be".format(city)
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

def getSunriseSunset(lat, lng, date):
    # https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&date=2017-07-31
    url = "https://api.sunrise-sunset.org/json?lat={}&lng={}&date={}".format(lat, lng, date)
    data = json.load(urllib2.urlopen(url))
    sunrise = data.get("results").get("sunrise").split()[0]
    sunset =  data.get("results").get("sunset").split()[0]
    timeZone = getTimeZone(lat, lng)
    return convertUTCtoLocal(date, sunrise, timeZone), convertUTCtoLocal(date, sunset, timeZone)


def convertUTCtoLocal(date, utcTime, timezone):
    to_zone = pytz.timezone(timezone)
    from_zone = _tz.gettz('UTC')
    utc = _datetime.strptime('%s %s' % (date, utcTime), '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    return timeConvert(str(local.time()))


# def getSunriseSunset(latitude, longitude, date):
#     """ provides sunrise and sunset time in 
#         local timezone of city whose longitude 
#         and latitude are given.

#         Args:
#             latitude (float): latitude location value
#             longitude (float): longitudnal location value

#         Returns:
#             (tuple): sunrise and sunset in standard time

#     """
#     # print date
#     url = "http://api.geonames.org/timezoneJSON?formatted=true&lat={}&lng={}&date={}&username=seaurchin".format(
#         latitude,
#         longitude,
#         date
#         )
#     try:
#         resp = urllib2.urlopen(url)
#     except Exception:
#         return (0, 0)

#     geoData = json.load(resp)
#     sunrise = geoData.get("sunrise").split()[-1]
#     sunset = geoData.get("sunset").split()[-1]
#     timezone = geoData.get("timezoneId")
#     return timeConvert(sunrise), timeConvert(sunset)

def getTimeZone(latitude, longitude):
    """ Provides timezone for a given longitude and latitude
    """
    # Note: We can also use this web service to get sunrise 
    # and sunset but due to inacuracy we use surise-sunset.org
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
    if request.method == "GET":
        searchCity = request.args.get("searchcity")
    else:
        searchCity = request.form.get("searchcity")

    if not searchCity:
        searchCity = request.cookies.get("last_search")

    if not searchCity:
            lat, lng, searchCity = getLongLatFromIP(getIP())


    try:
        weatherData = get_weather(searchCity)
    except Exception:
        return render_template("invalid_city.html", user_input=searchCity)
    data = json.loads(weatherData)
    try:
        city = data["city"]["name"]
    except KeyError:
        return render_template("invalid_city.html", user_input=searchCity)
    country = data["city"]["country"]

    lat = data["city"]["coord"]["lat"]
    lng = data["city"]["coord"]["lon"]
    forcast_list = []
    for d in data.get("list"):
        day = time.strftime('%G-%m-%d', time.localtime(d.get('dt')))
        mini = d.get("temp").get("min")
        maxi = d.get("temp").get("max")
        humid = d.get("humidity")
        desc = d.get("weather")[0].get("description")
        sunrise , sunset =  getSunriseSunset(lat, lng, day)
        forcast_list.append((day, mini, maxi, humid, desc, sunrise, sunset))
    response = make_response(render_template("index.html", forcast_list=forcast_list, 
        lat=lat, lng=lng, city=city,country=country))
    if request.args.get("remember"):
        response.set_cookie("last_search", "{},{}".format(city, country),
                expires=datetime.datetime.today() + datetime.timedelta(days=365))
    return response


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


