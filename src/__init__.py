# -*- coding: utf-8 -*-
__version__ = '0.2'
import sys
from flask import Flask

app = Flask('weatherApp')
app.config['SECRET_KEY'] = 'random'
from src.controller import *
