/**
 * Weather Charts JavaScript
 * Handles creation and updates of weather charts using Chart.js
 */

// Chart objects for reference
let temperatureChart = null;
let humidityChart = null;

/**
 * Initialize charts on page load
 */
function initCharts() {
    // Initialize temperature chart
    const tempCtx = document.getElementById('temperature-chart');
    if (tempCtx) {
        const initialData = extractTemperatureDataFromDOM();
        temperatureChart = createTemperatureChart(tempCtx, initialData);
    }
    
    // Initialize humidity chart
    const humidityCtx = document.getElementById('humidity-chart');
    if (humidityCtx) {
        const initialData = extractHumidityDataFromDOM();
        humidityChart = createHumidityChart(humidityCtx, initialData);
    }
}

/**
 * Creates a temperature chart
 */
function createTemperatureChart(canvas, data) {
    const units = document.getElementById('units-toggle')?.dataset?.units || 'metric';
    const tempUnit = units === 'metric' ? '°C' : '°F';
    
    return new Chart(canvas, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: `Temperature (${tempUnit})`,
                data: data.temperatures,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 3,
                fill: true
            }, {
                label: `Feels Like (${tempUnit})`,
                data: data.feelsLike,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Creates a humidity chart
 */
function createHumidityChart(canvas, data) {
    return new Chart(canvas, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Humidity (%)',
                data: data.humidity,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Extracts temperature data from the DOM
 */
function extractTemperatureDataFromDOM() {
    const forecastItems = document.querySelectorAll('.forecast-item');
    const labels = [];
    const temperatures = [];
    const feelsLike = [];
    
    // Add current weather
    const currentTemp = document.getElementById('current-temp')?.textContent;
    const currentFeelsLike = document.getElementById('feels-like')?.textContent;
    
    if (currentTemp) {
        labels.push('Now');
        temperatures.push(parseFloat(currentTemp));
        feelsLike.push(parseFloat(currentFeelsLike || currentTemp));
    }
    
    // Add forecast days
    forecastItems.forEach(item => {
        const day = item.querySelector('.forecast-day')?.textContent;
        const temp = item.querySelector('.forecast-temp')?.textContent;
        
        if (day && temp) {
            labels.push(day);
            // Remove the degree symbol
            temperatures.push(parseFloat(temp.replace('°', '')));
            // Use the same value for feels like since we don't have this data for forecast
            feelsLike.push(parseFloat(temp.replace('°', '')));
        }
    });
    
    return {
        labels,
        temperatures,
        feelsLike
    };
}

/**
 * Extracts humidity data from the DOM
 */
function extractHumidityDataFromDOM() {
    const labels = ['Current'];
    const humidity = [];
    
    // Get current humidity
    const currentHumidity = document.getElementById('humidity')?.textContent;
    if (currentHumidity) {
        humidity.push(parseFloat(currentHumidity));
    } else {
        humidity.push(0);
    }
    
    return {
        labels,
        humidity
    };
}

/**
 * Updates charts with new weather data
 */
function updateCharts(currentWeather, forecastData) {
    if (!currentWeather || !forecastData) return;
    
    // Update temperature chart
    if (temperatureChart) {
        const units = currentWeather.units;
        const tempUnit = units === 'metric' ? '°C' : '°F';
        
        // Update chart data
        temperatureChart.data.labels = ['Now'];
        temperatureChart.data.datasets[0].label = `Temperature (${tempUnit})`;
        temperatureChart.data.datasets[1].label = `Feels Like (${tempUnit})`;
        
        temperatureChart.data.datasets[0].data = [currentWeather.temperature];
        temperatureChart.data.datasets[1].data = [currentWeather.feels_like];
        
        // Add forecast data
        forecastData.forEach(day => {
            const date = new Date(day.date);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            
            temperatureChart.data.labels.push(dayName);
            temperatureChart.data.datasets[0].data.push(day.avg_temp);
            temperatureChart.data.datasets[1].data.push(day.avg_temp); // Use same value for feels like
        });
        
        temperatureChart.update();
    }
    
    // Update humidity chart
    if (humidityChart) {
        humidityChart.data.datasets[0].data = [currentWeather.humidity];
        humidityChart.update();
    }
}
