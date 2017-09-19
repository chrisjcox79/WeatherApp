import dataStruct as _ds
import utils as _utils
from model import getFieldValue
from timeUtils import timeConvert as _tc
from flask import request
from datetime import datetime as _datetime
import datetime


def dropVisitorTrackingCookie(response):
    """ drops visitor tacking session cookie and return the response object

        Arguments:
            response(request.make_response): response object
    """
    visitorId = request.cookies.get("unique_visitor")

    if not visitorId:
        visitorId = _ds.visitorInfo["visitorId"]
        # do not increment counter if visior has no left this domain name
        response.set_cookie("unique_visitor", visitorId,
            expires=_datetime.today() + datetime.timedelta(days=365))


    _ds.visitorInfo["visitorId"] = visitorId
    # we are keeping the cookie forever so we can track user
    # if he re-visit, just overwrite the same cookie with 
    # its existing value retrieved.
    dateTime = list(getFieldValue(
        "visitor", 'visitdatetime', 'visitorId', visitorId
        )
    )

    if not dateTime:
        return response

    dateTime = dateTime[0]
    time = _tc(dateTime.strftime('%H:%M:%S'))
    response.set_cookie(
        "{}_lastVisit".format(visitorId), dateTime.strftime(
            '%d-%m-%Y at {}'.format(time)
            )
        )

    return response