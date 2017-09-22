# -*- coding: utf-8 -*-
__version__ = '1.3.0'
import sys
import os
from flask import Flask
# from tzwhere import tzwhere as _tzwhere

# loading offline takes time so we load it one time and provide to whole app.
# tz = _tzwhere.tzwhere() # disabled as hobby-dev exceeds memory usage Heroku Error R14

app = Flask('weatherApp')

app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lfo6iwUAAAAAOe_vmVjdQbjzeBxM8imuIC3eJmo'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lfo6iwUAAAAANK_szhLcYcTjG51xcBwHXhjaJBb'
app.config["REDIS_HOST"] = os.getenv("REDIS_HOST")
app.config["REDIS_PORT"] = os.getenv("REDIS_PORT")
app.config["REDIS_PWD"] = os.getenv("REDIS_PWD", False)

import config

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Now that app object is available lets import everything from router
from src.router import *
