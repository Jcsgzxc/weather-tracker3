import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city):
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # For Celsius
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"]),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "feels_like": round(data["main"]["feels_like"]),
                "wind_speed": data["wind"]["speed"]
            }
        except requests.RequestException as e:
            return {"error": "Failed to fetch weather data. Please try again."}
        except (KeyError, ValueError) as e:
            return {"error": "Invalid city name. Please try again."} 