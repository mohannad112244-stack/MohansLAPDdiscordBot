import os
import requests

def get_la_weather():
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "⚠️ WeatherAPI key is missing."

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q=Los Angeles&aqi=no"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        condition = data['current']['condition']['text']
        temp = data['current']['temp_c']
        feels_like = data['current']['feelslike_c']
        return f"🌤️ LA Weather: **{condition}**, {temp}°C (feels like {feels_like}°C)."
    else:
        return "⚠️ Couldn't fetch LA weather. Try again later."
