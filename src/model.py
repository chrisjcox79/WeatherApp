
from src import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as _datetime

from flask_heroku import Heroku
heroku = Heroku(app)
db = SQLAlchemy(app)

class Messages(db.Model):
    __tablename__ = 'messages'
    msgId = db.Column('msg_id', db.Integer, primary_key=True)
    fullName = db.Column(db.String(60))
    message = db.Column(db.String)
    ip = db.Column(db.String(20))
    done = db.Column(db.Boolean)
    pub_date = db.Column(db.DateTime)
 
    def __init__(self, fullName, message, ip):
        self.fullName = fullName
        self.message = message
        self.ip = ip
        self.done = False
        self.pub_date = _datetime.utcnow()



class FingerprintVisitor(db.Model):
    __tablename__ = 'visitorinfo'
    visitor_id = db.Column("visitor_id", db.Integer, primary_key=True)
    platform = db.Column(db.String(15))
    browser = db.Column(db.String(10))
    cookiekey = db.Column(db.String(10))
    language = db.Column(db.String(10))
    version = db.Column(db.String(4))
    times = db.Column(db.Integer())
    ip = db.Column(db.String(20))

    def __init__(self, platform, browser, cookiekey, language, version, ip):
        self.platform = platform
        self.browser = browser
        self.cookiekey = cookiekey
        self.language = language
        self.version = version
        self.ip = ip

