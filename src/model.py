
from src import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as _datetime
from sqlalchemy import types
from sqlalchemy import schema

from flask_heroku import Heroku
heroku = Heroku(app)
db = SQLAlchemy(app)

class Messages(db.Model):
    __tablename__ = 'messages'
    msgId = db.Column('msg_id', db.Integer, primary_key=True)
    fullName = db.Column(db.String(60))
    message = db.Column(db.String)
    email = db.Column(db.String)
    visitorId = db.Column(db.String(10))
    done = db.Column(db.Boolean)
    pub_date = db.Column(types.Time(timezone=True)) 
 
    def __init__(self, fullName, email, message, visitorId, submitTime):
        self.fullName = fullName
        self.email = email
        self.message = message
        self.visitorId = visitorId
        self.done = False
        self.pub_date = submitTime



class FingerprintVisitor(db.Model):
    __tablename__ = 'visitorinfo'

    platform = db.Column(db.String(15))
    browser = db.Column(db.String(10))
    visitorId = db.Column(db.String(10), primary_key=True)
    language = db.Column(db.String(10))
    version = db.Column(db.String(20))
    times = db.Column(types.Integer(), autoincrement=True)
    ip = db.Column(db.String(20))
    visitor_time = db.Column(types.Time(timezone=True))

    def __init__(self, platform, browser, visitor_time, visitorId, language, version, ip):
        self.platform = platform
        self.browser = browser
        self.visitor_time = visitor_time
        self.visitorId = visitorId
        self.language = language
        self.version = version
        self.ip = ip


class TempTable(db.Model):
    __tablename__ = "tempTable"
    timeStamp = db.Column(types.Integer(), primary_key=True, autoincrement=True)
    moment = db.Column(types.Time(timezone=True)) 

    def __init__(self, tsz, moment):
        self.timeStamp = tsz
        self.moment = moment
