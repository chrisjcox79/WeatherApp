from src import app

from flask import Flask
from flask import render_template
from flask import request
from flask import make_response


from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, InputRequired

import timeUtils as _timeUtils
import utils as _utils


from dateutil import tz as _tz
import datetime
import pytz
from datetime import datetime as _datetime
import urllib2
import json


class CreateForm(FlaskForm):
    cityName = StringField('View forcast of city:', validators=[InputRequired()])
    count = IntegerField("Days")
    submit = SubmitField("Submit")


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
    url = _utils.getSunriseSunsetURL(lat, lng, date)
    data = _utils.getJsonFromURL(url)
    sunrise = data.get("results").get("sunrise").split()[0] # remove AM/PM from UTC time string
    sunset =  data.get("results").get("sunset").split()[0]
    return _timeUtils.convertUTCtoLocal(date, sunrise, timezone), _timeUtils.convertUTCtoLocal(date, sunset, timezone)


@app.route("/")
def index():
    searchCity = None
    lat = None
    lng = None
    count = None
    exactMatch = True
    timeZone = None
    if request.method == "GET":
        searchCity = request.args.get("searchcity")
    else:
        searchCity = request.form.get("searchcity")

    if not searchCity:
        searchCity = request.cookies.get("last_save_city")

    if not searchCity:
            lat, lng, searchCity = getLongLatFromIP(_utils.getIP())

    exactMatch = bool(request.args.get("exactMatch"))
    count = request.args.get("count") or request.cookies.get("count", 1)

    url = _utils.getWeatherURL(searchCity, count=count)
    data = _utils.getJsonFromURL(url)
    city = data["city"]["name"]
    if not isinstance(city , str):
        if data["city"]["name"] != searchCity and exactMatch:
            return render_template("invalid_city.html", user_input=searchCity)
        else:
             city = str(data["city"]["name"].encode("utf-8").encode('string-escape'))

    country = data["city"]["country"]

    if searchCity != city:
        render_template("invalid_city.html", user_input=searchCity)

    lat = lat or data["city"]["coord"]["lat"]
    lng = lng or data["city"]["coord"]["lon"]
    forcast_list = []
    timeZoneCookeName = "{}_{}_{}".format(city.lower(), lat, lng)
    timeZone = request.cookies.get(timeZoneCookeName)

    if timeZone:
        print "Retrieved %s cookie %s for city %s" % (timeZoneCookeName, request.cookies.get(timeZoneCookeName), city)
    else:
        timeZone = _timeUtils.getTimeZone(lat, lng)

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
        response.set_cookie("last_save_city", "{},{}".format(city.replace(" ", ""), country),
                expires=_datetime.today() + datetime.timedelta(days=365))
    response.set_cookie(timeZoneCookeName, timeZone,
            expires=_datetime.today() + datetime.timedelta(days=365))
    response.set_cookie("count", str(count),
            expires=_datetime.today() + datetime.timedelta(days=365))
    return response


