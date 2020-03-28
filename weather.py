from flask import Flask, render_template, request
import json
import urllib.request
import requests
import csv

api_key = 'e68e8e188344d2d59184b2b9ca8610c0'
country_dict = {}
with open('country.csv', 'r') as csvfile:
  csvreader = csv.reader(csvfile, delimiter=',')
  for row in csvreader:
    country_dict[row[1]] = row[0]
print(country_dict)
app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def weather():
  if request.method == 'POST':
    city = request.form['city']
    zipcode = request.form['zipcode']
    countrycode = request.form['countrycode']
    lat = request.form['lat']
    lon = request.form['lon']
  else:
    city = None
    zipcode = None
    countrycode = None
    data = requests.get('https://api.ipdata.co?api-key=test').json()
    lat = str(data['latitude'])
    lon = str(data['longitude'])
  
  # source contain json data from api
  if city:
    return byCity(city)
  elif zipcode and countrycode:
    return byZip(zipcode, countrycode)
  else:
    return byCoordinates(lat, lon)

@app.route('/', methods = ['POST', 'GET'])
def byCity(city):
  city = city.replace(' ', '%20')
  try:
    source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' + city + "&appid=" + api_key).read()
  except Exception as e:
    return render_template('index.html', error = str(e), byCity = True)
  weather_data = json.loads(source)
  data = { 
    "country_code": str(weather_data['sys']['country']), 
    "city_name" : str(weather_data['name']),
    "coordinate": str(weather_data['coord']['lat']) + ', ' 
                + str(weather_data['coord']['lon']), 
    "temp": "{:.2f}".format(weather_data['main']['temp'] - 273.16) + " °C", 
    "pressure": str(weather_data['main']['pressure']), 
    "humidity": str(weather_data['main']['humidity']) + "%", 
  }
  return render_template('index.html', data = data, byCity = True)

@app.route('/', methods = ['POST', 'GET'])
def byZip(zipcode, countrycode):
  if countrycode in country_dict.values():
    countrycode = list(country_dict.keys())[list(country_dict.values()).index(countrycode)]
  try:
    source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?zip=' + zipcode + ',' + countrycode + '&appid=' + api_key).read()
  except Exception as e:
    return render_template('index.html', error = str(e), byZipcode = True)
  weather_data = json.loads(source)
  data = { 
    "country_code": str(weather_data['sys']['country']), 
    "city_name" : str(weather_data['name']),
    "coordinate": str(weather_data['coord']['lat']) + ', ' 
                + str(weather_data['coord']['lon']), 
    "temp": "{:.2f}".format(weather_data['main']['temp'] - 273.16) + " °C", 
    "pressure": str(weather_data['main']['pressure']), 
    "humidity": str(weather_data['main']['humidity']) + "%", 
  }
  return render_template('index.html', data = data, byZipcode = True)

@app.route('/', methods = ['POST', 'GET'])
def byCoordinates(lat, lon):
  try:
    source = urllib.request.urlopen("http://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + api_key).read()
  except Exception as e:
    return render_template('index.html', error = str(e), byCoor = True)
  weather_data = json.loads(source)
  data = { 
    "country_code": str(country_dict[weather_data['sys']['country']] if weather_data['sys'].get('country') else 'Not a Country'), 
    "city_name" : str(weather_data['name']),
    "coordinate": str(weather_data['coord']['lat']) + ', ' 
                + str(weather_data['coord']['lon']), 
    "temp": "{:.2f}".format(weather_data['main']['temp'] - 273.16) + " °C", 
    "pressure": str(weather_data['main']['pressure']), 
    "humidity": str(weather_data['main']['humidity']) + "%", 
  }
  return render_template('index.html', data = data, byCoor = True)

if __name__ == '__main__': 
    app.run(debug = True) 