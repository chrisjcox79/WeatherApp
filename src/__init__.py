# -*- coding: utf-8 -*-
__version__ = '0.5.2'
import sys
import os
from flask import Flask

app = Flask('weatherApp')

app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lfo6iwUAAAAAOe_vmVjdQbjzeBxM8imuIC3eJmo'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lfo6iwUAAAAANK_szhLcYcTjG51xcBwHXhjaJBb'

import config

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Now that app object is available lets import controller
from src.controller import *
