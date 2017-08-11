# -*- coding: utf-8 -*-
__version__ = '0.3'
import sys

from flask import Flask

app = Flask('weatherApp')
app.config['SECRET_KEY'] = 'random'

app.config.from_pyfile('messages.cfg')
# Now that app object is available lets import controller
from src.controller import *
