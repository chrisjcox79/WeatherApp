from flask import Flask
from flask import render_template
from flask import request
import os
import urllib2
import json
import time

app = Flask(__name__)

def get_weather(city):
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt=10&mode=json&units=metric&appid=c0d8761ca979157a45651a5c7f12a6be".format(city)
    response = urllib2.urlopen(url).read()
    return response

@app.route("/")
def index():
    searchCity = request.args.get("searchcity")
    if not searchCity:
            searchCity = "Phillaur"
    try:
        weatherData = get_weather(searchCity)
    except Exception:
        return render_template("invalid_city.html", user_input=searchCity)
    data = json.loads(weatherData)
    try:
        city = data["city"]["name"]
    except KeyError:
        return render_template("invalid_city.html", user_input=searchCity)
    country = data["city"]["country"]

    forcast_list = []
    for d in data.get("list"):
        day = time.strftime('%d %B', time.localtime(d.get('dt')))
        mini = d.get("temp").get("min")
        maxi = d.get("temp").get("max")
        desc = d.get("weather")[0].get("description")
        forcast_list.append((day, mini, maxi, desc))
    return render_template("index.html", forcast_list=forcast_list, city=city, country=country)

@app.route("/hello/<name>/<int:age>")
def hello_name(name, age):
    return "Hello, {} you are {} year old.".format(name, age);

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


