# Weather Tracker Dashboard

A beautiful and responsive weather dashboard built with Python and Flet framework. The application fetches real-time weather data from OpenWeatherMap API and displays it in a user-friendly interface.

## Features

- Real-time weather data
- City search functionality
- Display of temperature, humidity, wind speed, and weather conditions
- Weather icons
- Responsive design for mobile and desktop
- Error handling and user feedback

## Setup

1. Clone this repository:
```bash
git clone <your-repo-url>
cd weather-tracker-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your OpenWeatherMap API key:
```
OPENWEATHERMAP_API_KEY=a04f51ae61fa023c383078ff96ccb40f
```

To get an API key:
1. Sign up at [OpenWeatherMap](https://openweathermap.org/)
2. Go to your account page
3. Generate an API key

## Running Locally

Run the application with:
```bash
python main.py
```

The app will open in your default web browser.

## Deployment

### Deploying to Replit

1. Create a new Python repl
2. Upload the project files
3. Add your OpenWeatherMap API key to the Secrets (Environment variables)
4. Install the dependencies from requirements.txt
5. Run the application

### Deploying to Render

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. Add your OpenWeatherMap API key as an environment variable
5. Deploy

## Contributing

Feel free to open issues and pull requests for any improvements you want to add.

## License

MIT License 