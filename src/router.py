from src import app

from flask import Flask 
from flask import render_template 
from flask import request 
from flask import flash 
from flask import jsonify 
from flask import make_response 

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




