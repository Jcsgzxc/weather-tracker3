/**
 * Weather Dashboard JavaScript
 * Handles UI interactions and dynamic updates
 */

// DOM elements
const searchForm = document.getElementById('search-form');
const locationInput = document.getElementById('location-input');
const refreshButton = document.getElementById('refresh-btn');
const locationSuggestions = document.getElementById('location-suggestions');
const loadingIndicator = document.getElementById('loading-indicator');
const errorContainer = document.getElementById('error-container');
const weatherContainer = document.getElementById('weather-container');
const forecastContainer = document.getElementById('forecast-container');
const lastUpdatedElement = document.getElementById('last-updated');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize search with autocomplete
    setupLocationAutocomplete();

    // Setup refresh button
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            refreshWeatherData();
        });
    }

    // Setup search form
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const location = locationInput.value.trim();
            if (location) {
                window.location.href = `/?location=${encodeURIComponent(location)}`;
            }
        });
    }

    // Initialize Chart.js charts
    initCharts();

    // Update the "last updated" timestamp
    updateLastUpdatedTime();
});

/**
 * Sets up autocomplete for location search
 */
function setupLocationAutocomplete() {
    if (!locationInput) return;
    
    let debounceTimeout;
    
    locationInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear previous timeout
        clearTimeout(debounceTimeout);
        
        // Hide suggestions if input is empty
        if (query.length < 2) {
            locationSuggestions.innerHTML = '';
            locationSuggestions.classList.add('d-none');
            return;
        }
        
        // Debounce API calls
        debounceTimeout = setTimeout(function() {
            // Show loading indicator in suggestions
            locationSuggestions.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div></div>';
            locationSuggestions.classList.remove('d-none');
            
            // Fetch suggestions from API
            fetch(`/api/location?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    locationSuggestions.innerHTML = '';
                    
                    if (data.error) {
                        locationSuggestions.innerHTML = `<div class="suggestion-item text-danger">Error: ${data.error}</div>`;
                        return;
                    }
                    
                    if (data.length === 0) {
                        locationSuggestions.innerHTML = '<div class="suggestion-item text-muted">No locations found</div>';
                        return;
                    }
                    
                    // Add each suggestion
                    data.forEach(location => {
                        const item = document.createElement('div');
                        item.className = 'suggestion-item';
                        item.textContent = location;
                        item.addEventListener('click', function() {
                            locationInput.value = location;
                            locationSuggestions.innerHTML = '';
                            locationSuggestions.classList.add('d-none');
                            searchForm.dispatchEvent(new Event('submit'));
                        });
                        locationSuggestions.appendChild(item);
                    });
                    
                    locationSuggestions.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('Error fetching location suggestions:', error);
                    locationSuggestions.innerHTML = '<div class="suggestion-item text-danger">Failed to fetch suggestions</div>';
                });
        }, 300); // 300ms debounce
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!locationInput.contains(e.target) && !locationSuggestions.contains(e.target)) {
            locationSuggestions.innerHTML = '';
            locationSuggestions.classList.add('d-none');
        }
    });
}

/**
 * Refreshes weather data via AJAX
 */
function refreshWeatherData() {
    // Show loading indicator
    if (loadingIndicator) {
        loadingIndicator.classList.remove('d-none');
    }
    
    // Hide error if shown
    if (errorContainer) {
        errorContainer.classList.add('d-none');
    }
    
    // Get current location and units from the page
    const location = document.getElementById('current-location')?.dataset?.location || 'New York';
    const units = document.getElementById('units-toggle')?.dataset?.units || 'metric';
    
    // Fetch updated weather data
    fetch(`/api/weather?location=${encodeURIComponent(location)}&units=${units}`)
        .then(response => response.json())
        .then(data => {
            if (loadingIndicator) {
                loadingIndicator.classList.add('d-none');
            }
            
            if (data.error) {
                showError(data.error);
                return;
            }
            
            // Update the UI with new data
            updateCurrentWeather(data.current_weather);
            updateForecast(data.forecast);
            updateCharts(data.current_weather, data.forecast);
            updateLastUpdatedTime();
        })
        .catch(error => {
            if (loadingIndicator) {
                loadingIndicator.classList.add('d-none');
            }
            showError('Failed to fetch weather data. Please try again.');
            console.error('Error refreshing weather data:', error);
        });
}

/**
 * Updates the current weather display
 */
function updateCurrentWeather(weatherData) {
    if (!weatherData || !weatherContainer) return;
    
    // Update temperature
    const tempElement = document.getElementById('current-temp');
    if (tempElement) {
        tempElement.textContent = weatherData.temperature;
    }
    
    // Update weather icon
    const iconElement = document.getElementById('current-weather-icon');
    if (iconElement) {
        iconElement.src = getWeatherIconUrl(weatherData.icon);
        iconElement.alt = weatherData.description;
    }
    
    // Update description
    const descElement = document.getElementById('current-weather-desc');
    if (descElement) {
        descElement.textContent = capitalizeFirstLetter(weatherData.description);
    }
    
    // Update feels like
    const feelsLikeElement = document.getElementById('feels-like');
    if (feelsLikeElement) {
        feelsLikeElement.textContent = weatherData.feels_like;
    }
    
    // Update humidity
    const humidityElement = document.getElementById('humidity');
    if (humidityElement) {
        humidityElement.textContent = weatherData.humidity;
    }
    
    // Update wind
    const windElement = document.getElementById('wind-speed');
    if (windElement) {
        windElement.textContent = weatherData.wind_speed;
    }
    
    // Update pressure
    const pressureElement = document.getElementById('pressure');
    if (pressureElement) {
        pressureElement.textContent = weatherData.pressure;
    }
}

/**
 * Updates the forecast display
 */
function updateForecast(forecastData) {
    if (!Array.isArray(forecastData) || !forecastContainer) return;
    
    // Clear existing forecast items
    forecastContainer.innerHTML = '';
    
    // Add new forecast items
    forecastData.forEach(day => {
        const date = new Date(day.date);
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const monthDay = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        
        const forecastItem = document.createElement('div');
        forecastItem.className = 'col forecast-item text-center p-3';
        forecastItem.innerHTML = `
            <div class="forecast-day fw-bold">${dayName}</div>
            <div class="forecast-date text-muted small mb-2">${monthDay}</div>
            <img src="${getWeatherIconUrl(day.icon)}" alt="${day.description}" class="forecast-icon mb-2" width="50">
            <div class="forecast-temp fw-bold">${day.avg_temp}°</div>
            <div class="forecast-desc small text-muted">${capitalizeFirstLetter(day.description)}</div>
        `;
        
        forecastContainer.appendChild(forecastItem);
    });
}

/**
 * Helper function to get weather icon URL
 */
function getWeatherIconUrl(iconCode) {
    return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
}

/**
 * Helper function to capitalize first letter of a string
 */
function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
 * Shows an error message
 */
function showError(message) {
    if (!errorContainer) return;
    
    errorContainer.textContent = message;
    errorContainer.classList.remove('d-none');
    
    if (weatherContainer) {
        weatherContainer.classList.add('d-none');
    }
}

/**
 * Updates the "last updated" timestamp
 */
function updateLastUpdatedTime() {
    if (!lastUpdatedElement) return;
    
    const now = new Date();
    lastUpdatedElement.textContent = now.toLocaleTimeString();
}

/**
 * Handles the unit toggle button
 */
document.addEventListener('DOMContentLoaded', function() {
    const unitToggle = document.getElementById('units-toggle');
    if (unitToggle) {
        unitToggle.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/toggle-units';
        });
    }
});
