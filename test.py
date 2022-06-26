import requests
from datetime import datetime
import config

def forecastWeather(city):
    user_api = config.weather_api_key
    location = city

    complete_api_link = "https://api.openweathermap.org/data/2.5/weather?q="+location+"&appid="+user_api
    api_link = requests.get(complete_api_link)
    api_data = api_link.json()

    try:
        #create variables to store and display data
        temp_city = ((api_data['main']['temp']) - 273.15)
        weather_desc = api_data['weather'][0]['description']
        hmdt = api_data['main']['humidity']
        wind_spd = api_data['wind']['speed']
        date_time = datetime.now().strftime("%d %b %Y ")#| %I:%M:%S %p

        forecast = f"-------------------------------------------------------------\n" \
                   f"Weather Stats for - {location.upper()}  || {date_time}\n" \
                   f"-------------------------------------------------------------\n" \
                   f"Current temperature is: {temp_city:.2f} deg C\n" \
                   f"Current weather desc  : {weather_desc}\n" \
                   f"Current Humidity      : {hmdt}%\n" \
                   f"Current wind speed    : {wind_spd} kmph"
        return temp_city,weather_desc,hmdt,wind_spd,date_time
        # print ("-------------------------------------------------------------")
        # print ("Weather Stats for - {}  || {}".format(location.upper(), date_time))
        # print ("-------------------------------------------------------------")
        #
        # print ("Current temperature is: {:.2f} deg C".format(temp_city))
        # print ("Current weather desc  :",weather_desc)
        # print ("Current Humidity      :",hmdt, '%')
        # print ("Current wind speed    :",wind_spd ,'kmph')
    except :
        return