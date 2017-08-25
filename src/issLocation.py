""" This module contains function to retireve International Space Station next flyby
"""

import requests
from datetime import datetime
import pytz
 
 
def get_next_pass(lat, lon):
    iss_url = 'http://api.open-notify.org/iss-pass.json'
    location = {'lat': lat, 'lon': lon}
    response = requests.get(iss_url, params=location).json()
 
    if 'response' in response:
        next_pass = response['response'][0]['risetime']
        next_pass_datetime = datetime.fromtimestamp(next_pass, tz=pytz.utc)
        print('Next pass for {}, {} is: {}'
              .format(lat, lon, next_pass_datetime))
        return next_pass_datetime
    else:
        print('No ISS flyby can be determined for {}, {}'.format(lat, lon))
