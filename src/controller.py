from src import app

from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import jsonify
from flask import make_response
from flask.views import View

import utils as _utils
import appforms as _appforms
import views as _views
import dataStruct as _ds
from model import db as _db
from model import updateOrInsertToTable

import math
import os
import datetime
import pytz
import urllib2
import json
from urllib import unquote
import timeUtils as _timeUtils
from datetime import datetime as _datetime


app.add_url_rule('/', view_func=_views.Index.as_view('index', template_name="index.html"))
app.add_url_rule('/newmsg', view_func=_views.Messaging.as_view('newmsg', template_name="index.html"))



@app.route("/citydatetime", methods=["POST"])
def getCityDateTime():
    data = request.get_json()

    if not data:
        return jsonify({"status": "No data to process."}), 201

    tz = data.get("tz")
    time, date = _utils.getCityDateTime(tz)
    return jsonify({"date": date, "time": _timeUtils.timeConvert(time)}), 200


@app.route("/regVisitor", methods=["POST"])
def registerVisitor():
    data = request.get_json()
    if not data:
        return jsonify({"status": "No data to process."}), 201

    visitorInfo = collectVisitorInfo(data)

    if bool(visitorInfo.get("increment", False)):
        if str(visitorInfo["referrer"]).find("searchCity") != -1 or visitorInfo["referrer"].endswith("newmsg"):
            return jsonify({"status": "coming from newmsg or SearchCity found"}), 200
        try:
            updateOrInsertToTable(request.user_agent, visitorInfo)
            return jsonify({"status" : "success"}), 200
        except Exception, er:
            return jsonify({"status": "fail:{}".format(er.message)})
    return jsonify({"status": "fail"}), 200


def collectVisitorInfo(data):

    url = data.get("referrer") # coming from javascript
    _ds.visitorInfo["clientIP"] = request.access_route[0]
    _ds.visitorInfo["increment"] = data.get("increment")
    _ds.visitorInfo["coord_errorcode"] = data.get("coord_errorcode")
    _ds.visitorInfo["referrer"] = unquote(url) if url else request.referrer
    _ds.visitorInfo["cl_lat"] = data.get("lat", request.cookies.get("cl_lat", 0.0))
    _ds.visitorInfo["cl_lng"] = data.get("long", request.cookies.get("cl_lng", 0.0))
    _ds.visitorInfo["language"] = data.get("language")
    _ds.visitorInfo["visitorId"] = request.cookies.get("unique_visitor")
    return _ds.visitorInfo


@app.route("/", methods=["POST", "GET"])
def index2():
    """ This function is the entry point for index page.
    """

    clientIP = request.access_route[0]
    hostIP = _utils.getHostIp()
    
    searchCity = None
    lat = None
    lng = None
    count = None
    exactMatch = True
    timeZone = None
    
    # visitorInfo = {}

    # first check if unique visitor id cookie exists else create unique visitor id
    unique_visitor_id = request.cookies.get("unique_visitor", _utils.id_generator())
    _ds.visitorInfo["visitorId"] = unique_visitor_id

    # always read latest date time visit from db and set cookie
    unique_visitor_lastVisit = request.cookies.get("{}_lastVisit".format(unique_visitor_id))

    _ds.visitorInfo["clientIP"] = clientIP

    if unique_visitor_lastVisit:
        flash("You last visited this site on %s" % " ".join(unique_visitor_lastVisit.split(" ")[:-1]))
    else:
        ## TODO read from db and set cookie
        pass
    count = request.args.get("count") or request.cookies.get("count", 1)
    form = _appforms.getSearchForcastForm(count)

    if request.method == "GET":
        searchCity = request.args.get("searchCity")
    else:
        searchCity = request.form.get("searchCity")

    if not searchCity:
        searchCity = request.cookies.get("last_searchCity")

    _ds.visitorInfo["cl_lat"] = request.args.get("lat", request.cookies.get("cl_lat"))
    _ds.visitorInfo["cl_lng"] = request.args.get("lng", request.cookies.get("cl_lng"))

    if not searchCity:
        ## lets get from googleapis geocode
        lat = float(request.cookies.get("cl_lat", 31.03))
        lng = float(request.cookies.get("cl_lng", 75.79))
        searchCity , country = _utils.getplace(lat, lng)
        searchCity = _utils.cityNameMap.get(searchCity, searchCity)
        searchCity = searchCity if searchCity else "Phillaur" # my hometown

    if not searchCity:
        lat, lng, searchCity = getLongLatFromIP(clientIP)

    # if clientIP in ('127.0.0.1', hostIP) or clientIP.startswith("192") and not searchCity:
    if clientIP in ('127.0.0.1', hostIP) and not searchCity:
        response = make_response(render_template("invalid_city.html", form=form, datetime = {}, title=" | Weather App", user_input="Home"))
        # response.set_cookie("client_lat", cl_lat)
        # response.set_cookie("client_lng", cl_lng)
        return __dropVisitorTrackingCookie(response)


    exactMatch = bool(request.args.get("exactMatch"))

    searchCity = searchCity.lower().capitalize() 

    jsonUrl = _utils.getWeatherURL(searchCity, count=count)
    data = _utils.getJsonFromURL(jsonUrl)

    if data.get("status", "pass") == "fail" or not data.get("city"):
        resp = make_response(render_template("invalid_city.html", form=form, datetime = {}, user_input=searchCity))
        return __dropVisitorTrackingCookie(resp)

    city = data["city"]["name"]

    if not isinstance(city , str):
        if city != searchCity and exactMatch:
            response = make_response(render_template("invalid_city.html", datetime = {}, form=form, title=" | Weather App", user_input=searchCity))
            # we are keeping the cookie forever so we can track him
            # and if he revisit, just overwrite the same cookie with its exisitng value retrieved.
            return __dropVisitorTrackingCookie(response)
        else:
             city = str(data["city"]["name"].encode("utf-8").encode('string-escape'))

    country = data["city"]["country"]

    if searchCity != city:
        resp = make_response(render_template("invalid_city.html", form=form, datetime={}, user_input=searchCity))
        resp.set_cookie("unique_visitor", unique_visitor_id)
        return resp

    lat = lat or data["city"]["coord"]["lat"]
    lng = lng or data["city"]["coord"]["lon"]
    forcast_list = []
    timeZoneCookeName = "{}_{}_{}".format(city.lower(), lat, lng)
    timeZone = request.cookies.get(timeZoneCookeName)

    if timeZone:
        print("Retrieved %s cookie %s for city %s" % (timeZoneCookeName, request.cookies.get(timeZoneCookeName), city))
    else:
        timeZone = _timeUtils.getTimeZone(lat, lng)

    key = os.getenv("GOOGLE_API_KEY")
    time, date = _utils.getCityDateTime(timeZone)
    dateTime = {
    "date": date,
    "time": _timeUtils.timeConvert(time),
    "timezone" : timeZone
    }

    weatherData = data.get("list")

    for d in weatherData:
        date = _datetime.fromtimestamp(d.get('dt')).strftime('%Y-%m-%d')
        mini = d.get("temp").get("min")
        maxi = d.get("temp").get("max")
        humid = "N/A" if d.get("humidity") == 0 else d.get("humidity")
        desc = d.get("weather")[0].get("description")
        sunrise , sunset =  getSunriseSunset(lat, lng, date, timeZone)
        forcast_list.append((date, mini, maxi, humid, desc, sunrise, sunset))
    
    # weather app starts index page
    response = make_response(
        render_template(
            "index.html", form = form, 
            forcast_list=forcast_list,
            lat=math.ceil(lat*100)/100, lng=math.ceil(lng*100)/100, city=city, key=key, datetime=dateTime,
            country=country, title=" | Weather App", count=count or request.cookies.get("count")
            )
        )

    response = __dropVisitorTrackingCookie(response)
    if request.args.get("remember"):
        response.set_cookie("last_searchCity", "{},{}".format(city.replace(" ", ""), " " + country),
                expires=_datetime.today() + datetime.timedelta(days=365))
    response.set_cookie(timeZoneCookeName, timeZone,
            expires=_datetime.today() + datetime.timedelta(days=365))
    response.set_cookie("count", str(count),
            expires=_datetime.today() + datetime.timedelta(days=365))
    return response


@app.route("/routerip", methods=["GET"])
def hostIpAddress():
    return jsonify({"hostIPAddress" : _utils.getHostIp()}), 200


@app.route("/providedIps", methods=["GET"])
def providedIps(): 
    return jsonify({"X-Forwarded-For" : request.headers.getlist("X-Forwarded-For")}), 200


@app.route("/accessroutes", methods=["GET"])
def accessRoute():
    return jsonify({"access_route" : request.access_route}), 200


@app.route("/useragent", methods=["GET"])
def userAgent():
    return jsonify({"user-agent": request.headers.get('User-Agent')}), 200


@app.route("/usragnt", methods=["GET"])
def reqUsrAgnt(): 
    return jsonify({"platform" : str(request.user_agent.platform)}), 200


@app.route("/uaatribs", methods=["GET"])
def uaatribs():
    return jsonify({"dir(request.user_agent)": dir(request.user_agent)}), 200


@app.route("/headers", methods=["GET"])
def toheader():
    return jsonify({"request.user_agent.to_header": dict(request.headers)}), 200


@app.route("/uastring", methods=["GET"])
def uastring():
    return jsonify({"request.user_agent.string": request.user_agent.string}), 200


@app.route("/requrl", methods=["GET"])
def requrl():
    return jsonify({"request.url_root": request.url_root }), 200




