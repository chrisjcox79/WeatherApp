""" this module contains time specific utility
    functions required by weather app.
"""

import pytz
import utils as _utils
from dateutil import tz as _tz
from datetime import datetime as _datetime

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
    url = _utils.getTimeZoneURL(latitude, longitude)
    geoData = _utils.getJsonFromURL(url)
    return geoData.get("timezoneId")
