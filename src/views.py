""" This module contains view implementations.
    http://flask.pocoo.org/docs/0.12/views/
"""

import os
import math
import urllib2
import pytz
import datetime

from src import app
# from src import redis
import utils as _utils
import dataStruct as _ds
import timeUtils as _timeUtils
import appforms as _appforms
import visitorTracking as _vt

from model import insertIntoTable

# from geodis import city as _gdcity
from flask import flash
from flask import request
from flask import make_response
from flask import render_template
from flask.views import View

from datetime import datetime as _datetime


class NotImplementedError(Exception):
    pass


class Messaging(View):
    """ View implementation for Messaging app
    """
    methods = ['GET', 'POST']

    def __init__(self, template_name):
        self.template_name = template_name

    def dispatch_request(self):
        form = _appforms.MessagingForm()

        if request.method == "POST":
            ip = request.access_route[0]
            tz = _utils.getTimezoneFromIP(ip)
            dtWithZone = datetime.datetime.now(pytz.timezone(tz))
            name = request.form.get('fullName', "")
            columValues = {
            'pub_date' : dtWithZone,  
            'fullName' : name,
            'visitorId': request.cookies.get("unique_visitor", ""),
            'message' : request.form.get('message', ""),
            'email' : request.form.get('email', "")
            }
            
            insertIntoTable(dtWithZone, 'messages', columValues)

            msg = "Thank you, {}".format(name)
            return render_template('thankyou.html', form=form, datetime={}, msg=msg)
        return render_template('newMessage.html', form=form, datetime={}, title=" | Messaging", msg="Write your message")


class Index(View):
    """ Implementation for weather app index page view.
    """

    def __init__(self, template_name):
        self.template_name = template_name
        self._dateTimeZone = {"show" : True}

    def get_template_name(self):
        raise NotImplementedError()

    def getCityWeatherForcast(self, searchCity, count=1):
        """ provides weather for city user searched for or retrieved from visitor ip

            Arguments:
                searchCity(str): city to get weather.

            Keyward Arguments:
                count(int): number of days to get weather for the city

            Returns:
                cityData(dict): dictionary of city data and city forcast.
        """
        cityData = {"city" : searchCity}
        lat = None
        lng = None
        exactMatch = bool(request.args.get("exactMatch"))

        searchCity = searchCity.lower().capitalize() 

        jsonUrl = _utils.getWeatherURL(searchCity, count=count)
        data = _utils.getJsonFromURL(jsonUrl)
        
        # when data retrieval fails from web service.
        if data.get("status", "pass") == "fail" or not data.get("city"):
            return cityData

        city = data["city"]["name"]

        if not isinstance(city, str):
            if city != searchCity and exactMatch:
                return cityData
            else:
                 city = str(data["city"]["name"].encode("utf-8").encode('string-escape'))

        cityData["city"] = city
        cityData["country"] = data["city"]["country"]

        if searchCity != city:
            return cityData

        lat = data["city"]["coord"]["lat"]
        lng = data["city"]["coord"]["lon"]
        forcast = []
        timeZoneCookeName = "{}_timezone".format(city.lower())
        timeZone = request.cookies.get(timeZoneCookeName)

        if timeZone:
            print("Retrieved %s cookie %s for city %s" % (timeZoneCookeName, request.cookies.get(timeZoneCookeName), city))
        else:
            timeZone = _timeUtils.getTimeZone(lat, lng)

        time, date = _utils.getCityDateTime(timeZone)

        self._dateTimeZone["date"] = date
        self._dateTimeZone["time"] = _timeUtils.timeConvert(time)
        self._dateTimeZone["timezone"] = timeZone

        if _utils.getJsonFromURL("http://ip-api.com/json/")["countryCode"] == cityData["country"]:
            self._dateTimeZone["show"] = False


        cityData["lat"] = lat
        cityData["lng"] = lng

        weatherData = data.get("list")

        for d in weatherData:
            date = _datetime.fromtimestamp(d.get('dt')).strftime('%Y-%m-%d')
            mini = d.get("temp").get("min")
            maxi = d.get("temp").get("max")
            humid = "N/A" if d.get("humidity") == 0 else d.get("humidity")
            desc = d.get("weather")[0].get("description")
            sunrise , sunset =  _timeUtils.getSunriseSunset(lat, lng, date, timeZone)
            forcast.append((date, mini, maxi, humid, desc, sunrise, sunset))

        cityData["forcast"] = forcast

        return cityData


    def dispatch_request(self):
        country = None
        searchCity = None
        count = request.args.get("count") or request.cookies.get("count", 1)
        form = _appforms.getSearchForcastForm(count)

        # first check if unique visitor id cookie exists else create unique visitor id
        unique_visitor_id = request.cookies.get("unique_visitor", _utils.id_generator())
        _ds.visitorInfo["visitorId"] = unique_visitor_id

        # always read latest date time visit from db and set cookie
        unique_visitor_lastVisit = request.cookies.get("{}_lastVisit".format(unique_visitor_id))
        _ds.visitorInfo["clientIP"] = _utils.getClientIp()

        if unique_visitor_lastVisit:
            flash("You last visited this site on %s" % " ".join(unique_visitor_lastVisit.split(" ")))

        if request.method == "GET":
            searchCity = request.args.get("searchCity")
        else:
            searchCity = request.form.get("searchCity")


        if not searchCity:
            searchCity = request.cookies.get("last_searchCity")

        _ds.visitorInfo["cl_lat"] = request.args.get("lat", request.cookies.get("cl_lat"))
        _ds.visitorInfo["cl_lng"] = request.args.get("lng", request.cookies.get("cl_lng"))

        if not searchCity:
            ## lets get lat long from cookie 
            lat = request.cookies.get("cl_lat")
            lng = request.cookies.get("cl_lng")
            if all([lat, lng]):
                # frsit try using geodis , faster based on redis
                # gd = _gdcity.City.getByLatLon(float(lat), float(lng), redis)
                
                # if not gd:
                #     from geodis.provider.geonames import GeonamesImporter
                #     import geodis
                #     fileName = os.path.split(geodis.__file__)[0] + "/data/cities1000.json"
                #     if os.path.exists(fileName):                    
                #         importer = GeonamesImporter(fileName, os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"), 0, redisPWD=os.getenv("REDIS_PWD"))
                #         importer.runImport()
                #     else:
                #         print "&" * 45
                #         print "cities1000.json does not exists. %s" % os.path.split(geodis.__file__)[0] 
                # else:
                #     searchCity, country = gd.name, gd.country

                # if fail to retireve from geodis, use web service
                # if not all([searchCity, country]):
                    # print "Failied to retireve city from geodis, attempting to use google api"              
                    # use googleapis geocode
                searchCity, country = _utils.getplace(lat, lng)
                #     searchCity = _utils.cityNameMap.get(searchCity, searchCity)
                # else:
                #     print "got data from geodis"
            else: # get lat long based on IP (may not be accurate)
                try:
                    lat, lng, searchCity = _utils.getLongLatFromIP(_ds.visitorInfo["clientIP"])
                except urllib2.URLError:
                    response = make_response(render_template("landing.html", form=form, datetime={}, title=" | Weather App", user_input="Home"))
                    return _vt.dropVisitorTrackingCookie(response)

        if not searchCity:
            response = make_response(render_template("landing.html", form=form, datetime={}, title=" | Weather App", user_input="Home"))
            return _vt.dropVisitorTrackingCookie(response)


        cityData = self.getCityWeatherForcast(searchCity, count=count)

        if cityData.get("forcast"):
            lat=math.ceil(cityData["lat"]*100)/100
            lng=math.ceil(cityData["lng"]*100)/100
            city=cityData["city"]
            response = make_response(
                render_template(self.template_name, form=form,
                    forcast_list=cityData["forcast"],
                    lat=lat,
                    lng=lng, 
                    city=city, key=os.getenv("GOOGLE_API_KEY"),
                    datetime=self._dateTimeZone,
                    country=cityData["country"], title=" | Weather App", 
                    count=count or request.cookies.get("count")
                    )
                )
            timeZoneCookeName = "{}_timezone".format(city.lower())
            response.set_cookie(timeZoneCookeName, self._dateTimeZone["timezone"],
                    expires=_datetime.today() + datetime.timedelta(days=365))
        else:
            response = make_response(
                render_template("landing.html", form=form, datetime = {}, user_input=searchCity))

        if request.args.get("remember"):
            response.set_cookie("last_searchCity", city,
                expires=_datetime.today() + datetime.timedelta(days=365))
        response.set_cookie("count", str(count),
                expires=_datetime.today() + datetime.timedelta(days=365))

        return _vt.dropVisitorTrackingCookie(response)


