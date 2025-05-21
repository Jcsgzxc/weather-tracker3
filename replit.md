# Weather Tracker Dashboard

## Overview

This repository contains a weather tracking web application built with Flask. The application fetches weather data from the OpenWeatherMap API and provides both a user interface and API endpoints to view current weather conditions and forecasts for different locations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

The application uses Flask as the web framework to serve both HTML pages and API endpoints. The main components include:

1. **Flask Web Server**: Handles HTTP requests, renders templates, and provides API endpoints.
2. **Weather Data Module**: Communicates with the OpenWeatherMap API to fetch current weather and forecast data.
3. **Caching System**: A simple in-memory caching system to reduce API calls and improve performance.

### Frontend Architecture

The frontend is built with HTML, CSS, and JavaScript, with a mobile-responsive design using Bootstrap 5:

1. **HTML Templates**: Using Flask's Jinja2 templating engine for dynamic content rendering.
2. **JavaScript**: Handles user interactions, AJAX calls to refresh data, and chart rendering.
3. **CSS**: Custom styling on top of Bootstrap for the weather interface.
4. **Chart.js**: For visualizing weather data in interactive charts.

## Key Components

### 1. Core Flask Application (`app.py`)

- Serves as the main controller handling routes and requests
- Manages sessions to remember user preferences (location, temperature units)
- Renders templates and returns API responses

### 2. Weather API Integration (`weather_api.py`)

- Fetches data from OpenWeatherMap API
- Supports both current weather and forecast data
- Handles location coordinates lookup
- Integrates with the caching system

### 3. Caching System (`cache.py`)

- Simple in-memory caching to reduce external API calls
- Implements expiration times for different types of data:
  - Current weather: 30 minutes
  - Forecast data: 1 hour
  - Location data: 24 hours

### 4. Frontend Components

- Responsive UI with Bootstrap 5
- Interactive charts for temperature and humidity using Chart.js
- Dynamic data refreshing via JavaScript
- SVG icons for weather conditions
- Location search with autocomplete suggestions

### 5. Server Application (`main.py`)

- Entry point for the application
- Configures and runs the Flask server
- Sets up logging for debugging

## Data Flow

1. **User Request Flow**:
   - User enters a location or uses their saved location
   - Flask controller processes the request
   - System checks the cache for existing data
   - If not in cache, external API call is made
   - Data is processed and cached
   - Response is rendered through templates

2. **API Request Flow**:
   - AJAX requests from frontend for data refreshing
   - Server processes request and checks cache
   - Returns JSON data to be rendered by JavaScript

3. **Caching Mechanism**:
   - Weather data is cached with appropriate expiration times
   - Subsequent requests use cached data if available
   - Cache is automatically cleared when data expires

## External Dependencies

### Backend Dependencies
- Flask: Web framework
- Requests: HTTP client for API calls
- Gunicorn: WSGI HTTP server for production deployment
- SQLAlchemy: ORM (included but not yet implemented)
- Psycopg2: PostgreSQL adapter (included but not yet implemented)
- Email-validator: For validating email addresses

### Frontend Dependencies
- Bootstrap 5: CSS framework for responsive design
- Chart.js: JavaScript library for interactive charts
- SVG icons: Custom icon set for weather conditions

### External Services
- OpenWeatherMap API: Primary source of weather data
  - Requires an API key (set in environment variables)
  - Provides current weather, forecasts, and geo-location services

## Deployment Strategy

The application is configured to be deployed on Replit with the following setup:

1. **Runtime Environment**:
   - Python 3.11
   - Stable Nix channel (24_05)
   - Required packages: OpenSSL, PostgreSQL

2. **Deployment Target**:
   - Autoscale configuration for dynamic resource allocation

3. **Run Command**:
   - Gunicorn WSGI server: `gunicorn --bind 0.0.0.0:5000 main:app`

4. **Workflow Configuration**:
   - Configured to run the main application on startup
   - Development mode uses hot reloading for code changes

5. **Database**:
   - PostgreSQL integration is configured but not yet implemented
   - SQLAlchemy is included for future ORM functionality

6. **Environment Variables**:
   - OpenWeather API key (`OPENWEATHER_API_KEY`)
   - Session secret (`SESSION_SECRET`)

### Future Improvements

1. **Database Integration**: Currently the application uses in-memory storage, but the foundations for PostgreSQL with SQLAlchemy are present.

2. **User Accounts**: Could be added to allow users to save multiple locations and preferences.

3. **Extended Forecast**: The API integration supports forecast data, which could be expanded beyond the current implementation.

4. **More Weather Data Points**: Additional metrics like air quality, UV index, and precipitation probability could be added.