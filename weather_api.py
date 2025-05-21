import os
import requests
import logging
from urllib.parse import quote
from cache import cache_data, get_cached_data

# OpenWeatherMap API key from environment
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"

# Cache expiration time (in seconds)
CACHE_EXPIRY = {
    'current': 30 * 60,  # 30 minutes
    'forecast': 60 * 60,  # 1 hour
    'location': 24 * 60 * 60  # 24 hours
}

def get_current_weather(location, units="metric"):
    """
    Get current weather data for a location
    
    Args:
        location (str): City name or coordinates
        units (str): 'metric' for Celsius, 'imperial' for Fahrenheit
        
    Returns:
        dict: Current weather data
    """
    # Check cache first
    cache_key = f"current_weather_{location}_{units}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        # First get coordinates if location is a string (city name)
        if not isinstance(location, tuple):
            coords = get_coordinates(location)
            if not coords:
                return {'error': f"Couldn't find location: {location}"}
            lat, lon = coords
        else:
            lat, lon = location
        
        # Make API request
        params = {
            'lat': lat,
            'lon': lon,
            'units': units,
            'appid': API_KEY
        }
        response = requests.get(f"{BASE_URL}/weather", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Format the data for our needs
        weather_data = {
            'location': data.get('name', location),
            'country': data.get('sys', {}).get('country', ''),
            'temperature': round(data.get('main', {}).get('temp', 0)),
            'feels_like': round(data.get('main', {}).get('feels_like', 0)),
            'humidity': data.get('main', {}).get('humidity', 0),
            'pressure': data.get('main', {}).get('pressure', 0),
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'wind_direction': data.get('wind', {}).get('deg', 0),
            'description': data.get('weather', [{}])[0].get('description', ''),
            'icon': data.get('weather', [{}])[0].get('icon', ''),
            'main': data.get('weather', [{}])[0].get('main', ''),
            'timestamp': data.get('dt', 0),
            'sunrise': data.get('sys', {}).get('sunrise', 0),
            'sunset': data.get('sys', {}).get('sunset', 0),
            'latitude': data.get('coord', {}).get('lat', 0),
            'longitude': data.get('coord', {}).get('lon', 0),
            'units': units
        }
        
        # Cache the data
        cache_data(cache_key, weather_data, CACHE_EXPIRY['current'])
        return weather_data
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API error in get_current_weather: {str(e)}")
        return {'error': f"Weather API error: {str(e)}"}
    except Exception as e:
        logging.error(f"Error in get_current_weather: {str(e)}")
        return {'error': f"An unexpected error occurred: {str(e)}"}

def get_forecast(location, units="metric"):
    """
    Get 5-day forecast data for a location
    
    Args:
        location (str): City name or coordinates
        units (str): 'metric' for Celsius, 'imperial' for Fahrenheit
        
    Returns:
        list: List of forecast data for each day
    """
    # Check cache first
    cache_key = f"forecast_{location}_{units}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        # First get coordinates if location is a string (city name)
        if not isinstance(location, tuple):
            coords = get_coordinates(location)
            if not coords:
                return {'error': f"Couldn't find location: {location}"}
            lat, lon = coords
        else:
            lat, lon = location
        
        # Make API request
        params = {
            'lat': lat,
            'lon': lon,
            'units': units,
            'appid': API_KEY
        }
        response = requests.get(f"{BASE_URL}/forecast", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process the data to get daily forecasts (OpenWeatherMap returns 3-hour forecasts)
        forecasts = data.get('list', [])
        
        # Group forecasts by day
        daily_forecasts = {}
        for forecast in forecasts:
            # Extract date (without time) from timestamp
            date = forecast.get('dt_txt', '').split(' ')[0] if 'dt_txt' in forecast else None
            if not date:
                continue
                
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'date': date,
                    'temps': [],
                    'icons': [],
                    'descriptions': []
                }
            
            # Add temperature for averaging later
            daily_forecasts[date]['temps'].append(forecast.get('main', {}).get('temp', 0))
            
            # Add weather icon and description
            if forecast.get('weather') and len(forecast.get('weather')) > 0:
                daily_forecasts[date]['icons'].append(forecast.get('weather')[0].get('icon', ''))
                daily_forecasts[date]['descriptions'].append(forecast.get('weather')[0].get('description', ''))
        
        # Calculate average temperatures and find most common icon/description for each day
        forecast_list = []
        for date, data in daily_forecasts.items():
            temps = data['temps']
            icons = data['icons']
            descriptions = data['descriptions']
            
            avg_temp = round(sum(temps) / len(temps)) if temps else 0
            
            # Find most common icon and description
            icon = max(set(icons), key=icons.count) if icons else ''
            description = max(set(descriptions), key=descriptions.count) if descriptions else ''
            
            forecast_list.append({
                'date': date,
                'avg_temp': avg_temp,
                'icon': icon,
                'description': description,
                'units': units
            })
        
        # Sort by date and limit to 5 days
        forecast_list.sort(key=lambda x: x['date'])
        forecast_list = forecast_list[:5]
        
        # Cache the data
        cache_data(cache_key, forecast_list, CACHE_EXPIRY['forecast'])
        return forecast_list
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API error in get_forecast: {str(e)}")
        return {'error': f"Weather API error: {str(e)}"}
    except Exception as e:
        logging.error(f"Error in get_forecast: {str(e)}")
        return {'error': f"An unexpected error occurred: {str(e)}"}

def get_coordinates(location):
    """
    Get coordinates (latitude, longitude) for a location name
    
    Args:
        location (str): City name
        
    Returns:
        tuple: (latitude, longitude) or None if not found
    """
    # Check cache first
    cache_key = f"coordinates_{location}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        # Make API request without double encoding
        params = {
            'q': location,  # The requests library will handle encoding properly
            'limit': 1,
            'appid': API_KEY
        }
        response = requests.get(GEO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            return None
            
        lat = data[0].get('lat')
        lon = data[0].get('lon')
        
        if lat is None or lon is None:
            return None
            
        coords = (lat, lon)
        
        # Cache the data
        cache_data(cache_key, coords, CACHE_EXPIRY['location'])
        return coords
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API error in get_coordinates: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error in get_coordinates: {str(e)}")
        return None

def get_location_data(query):
    """
    Get location data for autocomplete
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of location suggestions
    """
    # Check cache first
    cache_key = f"location_search_{query}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        # Make API request without double encoding
        params = {
            'q': query,  # The requests library will handle encoding properly
            'limit': 5,
            'appid': API_KEY
        }
        response = requests.get(GEO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Format the data
        locations = []
        for location in data:
            name = location.get('name', '')
            country = location.get('country', '')
            state = location.get('state', '')
            
            location_str = name
            if state:
                location_str += f", {state}"
            if country:
                location_str += f", {country}"
                
            locations.append(location_str)
            
        # Cache the data
        cache_data(cache_key, locations, CACHE_EXPIRY['location'])
        return locations
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API error in get_location_data: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error in get_location_data: {str(e)}")
        return []
