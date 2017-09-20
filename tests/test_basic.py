import os
import sys
import unittest
import stubout
import mox
sys.path.insert(0, os.getcwd())


from src import app
from src import utils as _utils
from src.model import db
from src import timeUtils as _timeUtils


mockData = {u'city': 
{
u'country': u'IN',
 u'population': 0,
 u'id': 1259775,
 u'coord': {u'lat': 31.0292,
 u'lon': 75.7842},
 u'name': u'Phillaur'},
 u'message': 4.410899,
 u'list': [{u'clouds': 0,
 u'temp': {u'min': 23.68,
 u'max': 34.04,
 u'eve': 32.79,
 u'morn': 34.04,
 u'night': 23.68,
 u'day': 34.04},
 u'humidity': 53,
 u'pressure': 988.76,
 u'weather': [{u'main': u'Clear',
 u'id': 800,
 u'icon': u'01d',
 u'description': u'sky is clear'}],
 u'dt': 1505887200,
 u'speed': 0.84,
 u'deg': 233}],
 u'cod': u'200',
 u'cnt': 1
 }

class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def test_index_page(self):
        self.mox = mox.Mox()
        self.mox.StubOutWithMock(_utils, "getClientIp")
        _utils.getClientIp().AndReturn(["127.0.0.1"])
        response = self.app.get('/', follow_redirects=True)
        self.addCleanup(self.mox.UnsetStubs)
        self.assertEquals(response.status_code, 200)

    def test_index_page_with_city(self):
        self.mox = mox.Mox()
        self.mox.StubOutWithMock(_utils, "getClientIp")
        _utils.getClientIp().AndReturn(["127.0.0.1"])
        # self.mox.StubOutWithMock(_timeUtils, "getTimeZone")
        # _timeUtils.getTimeZxone(31.0292, 75.7842).AndReturn("Asia/Kolkata")
        self.mox.StubOutWithMock(_utils, "getWeatherURL")
        _utils.getWeatherURL(u"Phillaur", count=u'1').AndReturn('/some/fake/URL')
        # self.mox.StubOutWithMock(_utils, "getJsonFromURL")
        # self.mox.StubOutWithMock(_utils.getJsonFromURL, "__call__")
        print _utils.getJsonFromURL.__call__("/some/fake/URL") # .AndReturn(mockData)
        # _utils.getJsonFromURL("/some/fake/URL").AndReturn(mockData)
        self.mox.ReplayAll()
        response = self.app.get('/?searchCity=Phillaur&count=1', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.mox.VerifyAll()

if __name__ == "__main__":
    unittest.main()
