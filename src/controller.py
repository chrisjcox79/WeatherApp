from src import app

from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import jsonify
from flask import make_response
import math
import os
from urllib import unquote
import timeUtils as _timeUtils
import utils as _utils
import appforms as _appforms
from model import Messages
from model import FingerprintVisitor
from model import db as _db
from model import insertIntoTable, getVisitorIdFromTable, updateOrInsertToTable

import datetime
import pytz
from datetime import datetime as _datetime
import urllib2
import json


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
    return (None, None, None)


def getCityFromMyIp(ip):
    """ fetch city based on user local public ip
    """
    geoloc = "http://ip-api.com/json/{}".format(ip)
    data = json.load(urllib2.urlopen(geoloc))
    return "Bangalore" if data.get("city") == "Bengaluru" else data.get("city")

@app.route("/regVisitor", methods=["GET"])
def registerVisitor():
    # do not increment if referrer is from same domain
    if request.url_root not in unquote(request.args.get("referrer")):
        try:
            visitorInfo = collectVisitorInfo()
            updateOrInsertToTable(request.user_agent, visitorInfo)
            return jsonify({"status" : "success"}), 200
        except Exception:
            return jsonify({"status": "fail"})
    else:
        return jsonify({"status" : "internal"}), 200

def collectVisitorInfo(uniqVistorId=None):
    visitorInfo = {}
    visitorInfo["clientIP"] = request.access_route[0]
    visitorInfo["referrer"] = unquote(request.args.get("referrer"))
    visitorInfo["cl_lat"] = request.args.get("lat", request.cookies.get("cl_lat", 0))
    visitorInfo["cl_lng"] = request.args.get("long", request.cookies.get("cl_lng", 0))
    visitorInfo["language"] = request.args.get("language")
    visitorInfo["visitorId"] = uniqVistorId or request.cookies.get("unique_visitor")
    return visitorInfo

def __dropVisitorTrackingCookie(response, visitorInfo):
    """ drops visitor tacking session cookie and return the response object

        Arguments:
            response(request.make_response): response object
    """

    visitorId =  visitorInfo["visitorId"]

    if not request.cookies.get("unique_visitor"):
        # do not increment counter if visior has no left this domain name
        response.set_cookie("unique_visitor", visitorId,
            expires=_datetime.today() + datetime.timedelta(days=365))

    # we are keeping the cookie forever so we can track user
    # if he re-visit, just overwrite the same cookie with 
    # its existing value retrieved.
    response.set_cookie("{}_lastVisit".format(visitorId))

    return response


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
    results = data.get("results")
    if not results:
        return "0:0", "0:0"
    sunrise = data.get("results").get("sunrise").split()[0] # remove AM/PM from UTC time string
    sunset =  data.get("results").get("sunset").split()[0]
    return _timeUtils.convertUTCtoLocal(date, sunrise, timezone), _timeUtils.convertUTCtoLocal(date, sunset, timezone)

@app.route("/", methods=["POST", "GET"])
def index():
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
    
    visitorInfo = {}

    # first check if unique visitor id cookie exists else create unique visitor id
    unique_visitor_id = request.cookies.get("unique_visitor", _utils.id_generator())
    visitorInfo["visitorId"] = unique_visitor_id
    unique_visitor_lastVisit = request.cookies.get("{}_lastVisit".format(unique_visitor_id))

    visitorInfo["clientIP"] = clientIP

    if unique_visitor_lastVisit:
        flash("You last visited this site on %s" % " ".join(unique_visitor_lastVisit.split(" ")[:-1]))

    count = request.args.get("count") or request.cookies.get("count", 1)
    form = _appforms.getSearchForcastForm(count)

    if request.method == "GET":
        searchCity = request.args.get("searchCity")
    else:
        searchCity = request.form.get("searchCity")

    if not searchCity:
        searchCity = request.cookies.get("last_searchCity")

    visitorInfo["cl_lat"] = request.args.get("lat", request.cookies.get("cl_lat"))
    visitorInfo["cl_lng"] = request.args.get("lng", request.cookies.get("cl_lng"))
    # if all(visitorInfo["cl_lat"], visitorInfo["cl_lng"]):

    # if clientIP in ('127.0.0.1', hostIP) or clientIP.startswith("192") and not searchCity:
    if clientIP in ('127.0.0.1', hostIP) and not searchCity:
        response = make_response(render_template("invalid_city.html", form=form, title=" | Weather App", user_input="Home"))
        # response.set_cookie("client_lat", cl_lat)
        # response.set_cookie("client_lng", cl_lng)
        return __dropVisitorTrackingCookie(response, visitorInfo)

    if not searchCity:
        lat, lng, searchCity = getLongLatFromIP(clientIP)

    if not searchCity:
        lat, lng, searchCity = 31.03, 75.79, "Phillaur"

    exactMatch = bool(request.args.get("exactMatch"))

    searchCity = searchCity.lower().capitalize() 

    jsonUrl = _utils.getWeatherURL(searchCity, count=count)
    data = _utils.getJsonFromURL(jsonUrl)

    if data.get("status", "pass") == "fail" or not data.get("city"):
        resp = make_response(render_template("invalid_city.html", form=form, user_input=searchCity))
        return __dropVisitorTrackingCookie(resp, visitorInfo)

    city = data["city"]["name"]

    if not isinstance(city , str):
        if city != searchCity and exactMatch:
            response = make_response(render_template("invalid_city.html", form=form, title=" | Weather App", user_input=searchCity))
            # we are keeping the cookie forever so we can track him
            # and if he revisit, just overwrite the same cookie with its exisitng value retrieved.
            return __dropVisitorTrackingCookie(response, visitorInfo)
        else:
             city = str(data["city"]["name"].encode("utf-8").encode('string-escape'))

    country = data["city"]["country"]

    if searchCity != city:
        resp = make_response(render_template("invalid_city.html", form=form, user_input=searchCity))
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

    for d in data.get("list"):
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
            lat=math.ceil(lat*100)/100, lng=math.ceil(lng*100)/100, city=city, key=key,
            country=country, title=" | Weather App", count=count or request.cookies.get("count")
            )
        )

    response = __dropVisitorTrackingCookie(response, visitorInfo)
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


@app.route('/newmsg', methods=['GET', 'POST'])
def newmsg():
    form = _appforms.MessagingForm()
    # if form.validate_on_submit():
    if request.method == "POST":
        ip = request.access_route[0]
        data = _utils.getJsonFromURL("http://ip-api.com/json/{}".format(ip))
        tz = "Asia/Kolkata"
        if data["status"] == "success":
            tz = data["timezone"]

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
        return render_template('thankyou.html', form=form, msg=msg)
    return render_template('newMessage.html', form=form, title=" | Messaging", msg="Write your message")



