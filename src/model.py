
from src import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as _datetime
from sqlalchemy import types, Integer
from sqlalchemy import schema, Sequence
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from flask_heroku import Heroku
import utils as _utils
import pytz
from sqlalchemy import create_engine
from sqlalchemy import DateTime

heroku = Heroku(app)
db = SQLAlchemy(app)

USER_ID_SEQ = Sequence('user_id_seq')  # define sequence explicitly



def updateOrInsertToTable(user_agent, visitorInfo):
    """ 
        Arguments: 
            user_agent (request.user_agent): request.user_agent object
            visitorInfo (dict): key value pair of visitor information 


    """
    visitorId =  visitorInfo["visitorId"]
    visitorIp = visitorInfo["clientIP"]
    language = visitorInfo["language"]
    referrer = visitorInfo["referrer"]
    coord_errorcode = visitorInfo.get("coord_errorcode", None)
    cl_lat = visitorInfo.get("cl_lat", 0.0)
    cl_lng = visitorInfo.get("cl_lng", 0.0)
    data = _utils.getJsonFromURL("http://ip-api.com/json/{}".format(visitorIp))
    tz = "UTC"
    if data["status"] == "success":
        tz = data["timezone"]
    dtWithZone = _datetime.now(pytz.timezone(tz))
    visitorModel = Visitor(
        user_agent.platform,
        user_agent.browser, 
        dtWithZone, visitorId, 
        cl_lat, cl_lng,
        language, referrer,
        user_agent.version, 
        visitorIp,
        tz
    )
    existing = visitorModel.query.get(visitorId)

    if existing:
        existing.version = user_agent.version
        existing.cl_lat = float(cl_lat)
        existing.cl_lng = float(cl_lng)
        existing.ip = visitorIp
        existing.language = language
        existing.referrer = referrer
        if referrer == "":
            existing.count = existing.count + 1
        existing.coord_errorcode = coord_errorcode
        existing.visitdatetime = dtWithZone
        db.session.commit()
    else:
        columnValues = {
            "platform" : user_agent.platform,
            "browser" : user_agent.browser,
            "visitorId" : visitorId,
            "cl_lat" : cl_lat,
            "cl_lng" : cl_lng,
            "language" : user_agent.language,
            "referrer" : referrer,
            "version" : user_agent.version,
            "count" : 1,
            "coord_errorcode": coord_errorcode,
            "ip" : visitorIp,
            "visitdatetime" : dtWithZone,
            "timezone": tz
        }
        insertIntoTable(dtWithZone, 'visitor', columnValues)



def insertIntoTable(dtWithZone, tableName, columValues):
    """ Insert into table with provided date time and time zone information.
    """
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    engine = create_engine(db_uri, connect_args={"options": "-c timezone={}".format(dtWithZone.timetz().tzinfo.zone)})
    meta = MetaData(engine, reflect=True)
    table = meta.tables[tableName]
    ins = table.insert().values(**columValues)
    conn = engine.connect()
    conn.execute(ins)
    conn.close()


class Messages(db.Model):
    __tablename__ = 'messages'

    msgId = db.Column('msg_id', db.Integer, autoincrement=True, primary_key=True)
    fullName = db.Column(db.String(60))
    message = db.Column(db.String)
    email = db.Column(db.String)
    visitorId = db.Column(db.String(10), db.ForeignKey("visitor.visitorId"))
    # ip = db.relationship('visitor', backref='info', lazy='dynamic')
    pub_date = db.Column(DateTime(timezone=True)) 
 
    def __init__(self, fullName, email, message, visitorId, submitTime):
        self.fullName = fullName
        self.email = email
        self.message = message
        self.visitorId = visitorId
        self.pub_date = submitTime



class Visitor(db.Model):
    __tablename__ = 'visitor'

    visitorId = db.Column(db.String(10), primary_key=True)
    platform = db.Column(db.String(15))
    browser = db.Column(db.String(10))
    language = db.Column(db.String(10))
    version = db.Column(db.String(20))
    cl_lat = db.Column(types.Float(25), nullable=True)
    cl_lng = db.Column(types.Float(25), nullable=True)
    count = db.Column(Integer)
    referrer = db.Column(db.String(150), nullable=True)
    ip = db.Column(db.String(20))
    coord_errorcode = db.Column(db.Integer, nullable=True)
    visitdatetime = db.Column(DateTime(timezone=True))
    timezone = db.Column(db.String(24))

    def __init__(self, platform, browser, visitor_time, timezone, visitorId, lat, lng, language, referrer, version, ip):
        self.platform = platform
        self.browser = browser
        self.timezone = timezone
        self.visitor_time = visitor_time
        self.visitorId = visitorId
        self.cl_lat = lat
        self.cl_lng = lng
        self.language = language
        self.referrer = referrer
        self.version = version
        self.ip = ip


class TempTable(db.Model):
    __tablename__ = "tempTable"
    timeStamp = db.Column(types.Integer(), primary_key=True, autoincrement=True)
    moment = db.Column(types.Time(timezone=True)) 

    def __init__(self, tsz, moment):
        self.timeStamp = tsz
        self.moment = moment


class City(object):
    def __init__(self, key, name, lat, lng):
        self.key  = key
        self.name = name
        self.lat  = lat
        self.lng  = lng


