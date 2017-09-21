# -*- coding: utf-8 -*-
__version__ = '1.1.4'
import sys
import os
from flask import Flask
from redis import Redis
app = Flask('weatherApp')

app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lfo6iwUAAAAAOe_vmVjdQbjzeBxM8imuIC3eJmo'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lfo6iwUAAAAANK_szhLcYcTjG51xcBwHXhjaJBb'
app.config["REDIS_HOST"] = os.getenv("REDIS_HOST")
app.config["REDIS_PORT"] = os.getenv("REDIS_PORT")
app.config["REDIS_PWD"] = os.getenv("REDIS_PWD", False)

import config

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print "R" * 50
print app.config["REDIS_PWD"]
print "D" * 50

if bool(app.config["REDIS_PWD"]):
	redis = Redis(app.config["REDIS_HOST"], port=app.config["REDIS_PORT"],
	db=0, password=app.config["REDIS_PWD"])
else:
	redis = Redis(app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=0)

# Now that app object is available lets import everything from router
from src.router import *
