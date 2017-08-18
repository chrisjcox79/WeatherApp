# -*- coding: utf-8 -*-
__version__ = '0.3.1'
import sys
import os
from flask import Flask

app = Flask('weatherApp')

app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lfo6iwUAAAAAOe_vmVjdQbjzeBxM8imuIC3eJmo'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lfo6iwUAAAAANK_szhLcYcTjG51xcBwHXhjaJBb'
# print "*" * 50
import config
# print dir(config)
app.config.from_object(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# app.config['SECRET_KEY'] = 'random'
# app.config.from_pyfile('messages.cfg')

# Now that app object is available lets import controller
from src.controller import *
