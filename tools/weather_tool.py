import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather_conditions(lat: float, lon: float) -> dict:
        api_key = os.getenv('openweather_api_key')
        
        url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?lat={lat}&lon={lon}"
                f"&appid={api_key}"
                f"&units=imperial"
        )

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return {
                'temperature': data['main']['temp'],
                'feels like': data['main']['feels_like'],
                'pressure': data['main']['pressure'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind']['deg'],
                'conditions': data['weather'][0]['description'],
                'location_name': data['name']
        }



 

