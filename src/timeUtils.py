""" this module contains time specific utility
    functions required by weather app.
"""

import pytz
import utils as _utils
from dateutil import tz as _tz
from datetime import datetime as _datetime


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
    sunrise = data.get("results").get("sunrise") #.split()[0] # remove AM/PM from UTC time string
    sunset =  data.get("results").get("sunset")#.split()[0]
    return (
        convertUTCtoLocal(
            date, 
            sunrise, 
            timezone
            ),
        convertUTCtoLocal(
            date, 
            sunset,
            timezone
            )
        )



def timeConvert(militaryTime):
    """ convert millitary time to standard time.
    """
    hours, minutes, seconds = militaryTime.split(":")
    if not all([hours, minutes, seconds]):
        return ""
    try:
        hours, minutes, seconds = int(hours), int(minutes), int(seconds)
    except ValueError, er:
        print hours, minutes, seconds
        return ""
    setting = " AM"
    if hours > 12:
        setting = " PM"
        hours -= 12
    if hours == 0:
        hours = 12
    return "%02d:%02d"  % (hours, minutes) + setting


def convertUTCtoLocal(date, utcTime, timezone):
    """ converts UTC time to given timezone
    """
    to_zone = pytz.timezone(timezone)
    from_zone = _tz.gettz('UTC')
    ## for formating with AM and PM hours in strptime you need to add
    ## %p at the end, also instead of %H you need to use %I
    utc = _datetime.strptime('%s %s' % (date, utcTime), '%Y-%m-%d %I:%M:%S %p')
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    return timeConvert(str(local.time()))


def getTimeZone(latitude, longitude):
    """ Provides timezone for a given longitude and latitude
    """
    # Note: We can also use this web service to get sunrise 
    # and sunset but due to inacuracy we use surise-sunset.org
    print("getting time zone from web service")
    url = _utils.getTimeZoneURL(latitude, longitude)
    geoData = _utils.getJsonFromURL(url)
    return geoData.get("timezoneId")
