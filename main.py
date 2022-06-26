# Importing essential libraries and modules

from flask import Flask, render_template, request
import numpy as np
import pickle
import config
import requests
from test import forecastWeather
from location import getLocation
import warnings
warnings.filterwarnings('ignore')
# ==============================================================================================

# -------------------------LOADING THE TRAINED MODELS -----------------------------------------------

# Loading crop recommendation model

crop_recommendation_model_path = 'models/RandomForest.pkl'
crop_recommendation_model = pickle.load(open(crop_recommendation_model_path, 'rb'))

# ===============================================================================================

# -------------------------Weather Forecast-----------------------------------------------

# Geting Wheather details of the city
def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None

def weather_forecast(city_name):
    # city_name = "berlin"  # you can ask for user input instead
    api_key = config.weather_api_key

    # Let's get the city's coordinates (lat and lon)
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
    # print(url)

    # Let's parse the Json
    req = requests.get(url)
    data = req.json()

    # Let's get the name, the longitude and latitude
    name = data['name']
    lon = data['coord']['lon']
    lat = data['coord']['lat']

    # print(name, lon, lat)
    # Let's now use the One Call Api to get the 8 day forecast
    # We'll need to exclude the minutely and hourly
    exclude = "minute,hourly"

    url2 = f'https://api.openweather.map.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid{api_key}'
    # print(url2)

    # Let's now parse the JSON
    req2 = requests.get(url2)
    data2 = req2.json()
    # print(data2)

    # Let's now get the temp for the day, the night and the weather conditions
    days = []
    nights = []
    descr = []

    # We need to access 'daily'
    for i in data2['daily']:
        # We notice that the temperature is in Kelvin, so we need to do -273.15 for every datapoint

        # Let's start by days
        # Let's round the decimal numbers to 2
        days.append(round(i['temp']['day'] - 273.15, 2))

        # Nights
        nights.append(round(i['temp']['night'] - 273.15, 2))

        # Let's now get the weather condition and the description
        # 'weather' [0] 'main' + 'weather' [0] 'description'
        descr.append(i['weather'][0]['main'] + ": " + i['weather'][0]['description'])

    # print(days)
    # print(nights2)
    # print(descr)
    # Let's now format the output to make it readable
    string = f'[ {name} - 8 days forecast]\n'

    # Let's now loop for as much days as there available (8 in this case):
    for i in range(len(days)):

        # We want to print out the day (day1,2,3,4..)
        # Also, day 1 = today and day 2 = tomorrow for reference

        if i == 0:
            string += f'\nDay {i + 1} (Today)\n'

        elif i == 1:
            string += f'\nDay {i + 1} (Tomorrow)\n'

        else:
            string += f'\nDay {i + 1}\n'

        string += 'Morning:' + str(days[i]) + '°C' + "\n"
        string += 'Night:' + str(nights[i]) + '°C' + "\n"
        string += 'Conditions:' + descr[i] + '\n'

    return string




# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)


# render home page
@app.route('/')
def home():
    title = 'Final Year Project - Home'
    return render_template('index.html', title=title)


# render crop recommendation form page
@app.route('/crop-recommend')
def crop_recommend():
    title = 'Crop Recommendation'
    return render_template('crop.html', title=title)


# ===============================================================================================

# RENDER PREDICTION PAGE
# render crop recommendation result page
@app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    title = 'Crop Recommendation'
    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        temperature = float(request.form['Temparature'])
        humidity = float(request.form['Humidity'])
        # state = request.form.get("stt")
        city = request.form.get("city")
        latitude , longitude = getLocation()
        # temperature, humidity = weather_fetch(city)
        feat = [N, P, K, temperature, humidity, ph, rainfall]
        # url = 'https://wttr.in/{}'.format(city)
        # res = requests.get(url)
        # w_for = res.text.encode('utf-8')
        if forecastWeather(city) == None:
            return render_template('try_again.html', string=f"{city} Data not available", title=title)

        temp_city , weather_desc, hmdt, wind_spd, date_time = forecastWeather(city)
        temp = "{:.2f}".format(temp_city)
        # threedays = weather_forecast(city)


        # display the result!

        # label = min - max (values)
        # N = 0 - 140 mg/KG
        # P = 5 - 145
        # K = 5 - 205
        # ph = 3.5 - 10
        # rainfall = 20 - 289.56 mm
        # temperature =8.8 - 44 C
        # humidity =  14 - 100 %
        flag = 0
        s = "Enter Valid "
        if N < 0 or N > 200:
            s += "  Nitrogen data "
            flag += 1
        if P < 5 or P > 200:
            s += "  Phosphorous data "
            flag += 1
        if K < 5 or K > 205:
            s += "  Pottasium data "
            flag += 1
        if temperature < 8.8 or temperature > 48:
            s += "  Temparature data "
            flag += 1
        if humidity < 5 or humidity > 100:
            s += "  Humidity data "
            flag += 1
        if ph < 3 or ph > 11:
            s += "  ph data "
            flag += 1
        if rainfall < 0 or rainfall > 300:
            s += "  Rainfall data "
            flag += 1

        if flag == 0:
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction, title=title,
                                    temp_city=temp , weather_desc= weather_desc,
                                   hmdt=hmdt, wind_spd= wind_spd, date_time =date_time,location = city.upper(),
                                   lat= latitude, lon = longitude)

        else:

            return render_template('try_again.html', string=s, title=title)


# ===============================================================================================
if __name__ == '__main__':
    app.run()
