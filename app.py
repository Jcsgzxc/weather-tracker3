import os
import logging
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from weather_api import get_current_weather, get_forecast, get_location_data
from database import db

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "517fcff6c2c88dbc02c3e3e60eb49e328b28ddd1dcb1b1cc0669a732a964a4a6")

# Set OpenWeather API key
os.environ["OPENWEATHER_API_KEY"] = "YOUR_API_KEY_HERE"  # Replace with your actual API key from OpenWeatherMap

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize app with the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Add custom filters
@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    """Convert Unix timestamp to formatted date"""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

@app.template_filter('to_day_name')
def to_day_name(date_str):
    """Convert date string to day name"""
    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%a')

@app.template_filter('to_month_day')
def to_month_day(date_str):
    """Convert date string to month and day"""
    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%b %d')

# Default location (New York)
DEFAULT_LOCATION = "New York"
DEFAULT_UNITS = "metric"  # 'metric' for Celsius, 'imperial' for Fahrenheit

@app.route('/')
def index():
    """Render the main page with weather information"""
    # Get location from query parameter, session, or default
    location = request.args.get('location') or session.get('location', DEFAULT_LOCATION)
    units = request.args.get('units') or session.get('units', DEFAULT_UNITS)
    
    # Store in session
    session['location'] = location
    session['units'] = units
    
    try:
        # Get weather data
        current_weather = get_current_weather(location, units)
        forecast_data = get_forecast(location, units)
        
        # Check if data was successfully retrieved
        if not current_weather or 'error' in current_weather:
            return render_template('error.html', error=current_weather.get('error', 'Failed to fetch weather data'))
        
        return render_template('index.html', 
                              current_weather=current_weather, 
                              forecast=forecast_data,
                              location=location,
                              units=units)
    except Exception as e:
        logging.error(f"Error fetching weather data: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/api/weather')
def api_weather():
    """API endpoint for AJAX calls to refresh weather data"""
    location = request.args.get('location', DEFAULT_LOCATION)
    units = request.args.get('units', DEFAULT_UNITS)
    
    try:
        current_weather = get_current_weather(location, units)
        forecast_data = get_forecast(location, units)
        
        if not current_weather or 'error' in current_weather:
            return jsonify({'error': current_weather.get('error', 'Failed to fetch weather data')})
        
        return jsonify({
            'current_weather': current_weather,
            'forecast': forecast_data
        })
    except Exception as e:
        logging.error(f"API Error: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/api/location')
def api_location():
    """API endpoint for location search suggestions"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    try:
        locations = get_location_data(query)
        return jsonify(locations)
    except Exception as e:
        logging.error(f"Location API Error: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/toggle-units')
def toggle_units():
    """Toggle between metric and imperial units"""
    current_units = session.get('units', DEFAULT_UNITS)
    new_units = 'imperial' if current_units == 'metric' else 'metric'
    session['units'] = new_units
    
    # Redirect back to the main page with the new units
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error="Page not found"), 404

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        from models import User
        
        if not username or not email or not password or not confirm_password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
            
        # Create new user
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.password_hash = generate_password_hash(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error registering user: {str(e)}")
            flash('An error occurred during registration', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        from models import User
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            
            # Store the user's unit preference in the session
            session['units'] = user.default_units
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    from models import FavoriteLocation
    
    # Get user's favorite locations
    favorites = FavoriteLocation.query.filter_by(user_id=current_user.id).order_by(FavoriteLocation.added_at.desc()).all()
    
    return render_template('profile.html', favorites=favorites)

@app.route('/favorites/add', methods=['POST'])
@login_required
def add_favorite():
    """Add a location to favorites"""
    location_name = request.form.get('location_name')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    
    if not location_name:
        flash('Location name is required', 'danger')
        return redirect(url_for('index'))
    
    from models import FavoriteLocation
    
    # Check if already in favorites
    existing = FavoriteLocation.query.filter_by(
        user_id=current_user.id,
        location_name=location_name
    ).first()
    
    if existing:
        flash(f'{location_name} is already in your favorites', 'info')
        return redirect(url_for('index'))
    
    # Add to favorites
    try:
        favorite = FavoriteLocation()
        favorite.user_id = current_user.id
        favorite.location_name = location_name
        favorite.latitude = float(latitude) if latitude else None
        favorite.longitude = float(longitude) if longitude else None
        db.session.add(favorite)
        db.session.commit()
        flash(f'{location_name} added to favorites', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding favorite: {str(e)}")
        flash('An error occurred while adding to favorites', 'danger')
    
    return redirect(url_for('index'))

@app.route('/favorites/remove/<int:favorite_id>', methods=['POST'])
@login_required
def remove_favorite(favorite_id):
    """Remove a location from favorites"""
    from models import FavoriteLocation
    
    favorite = FavoriteLocation.query.get_or_404(favorite_id)
    
    # Check if the favorite belongs to the current user
    if favorite.user_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('profile'))
    
    try:
        location_name = favorite.location_name
        db.session.delete(favorite)
        db.session.commit()
        flash(f'{location_name} removed from favorites', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error removing favorite: {str(e)}")
        flash('An error occurred while removing from favorites', 'danger')
    
    return redirect(url_for('profile'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    if request.method == 'POST':
        default_units = request.form.get('default_units')
        
        if default_units not in ['metric', 'imperial']:
            flash('Invalid units selection', 'danger')
            return redirect(url_for('settings'))
        
        try:
            current_user.default_units = default_units
            db.session.commit()
            session['units'] = default_units
            flash('Settings updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating settings: {str(e)}")
            flash('An error occurred while updating settings', 'danger')
    
    return render_template('settings.html')

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error="Internal server error"), 500
