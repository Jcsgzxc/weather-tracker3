import datetime
from flask_login import UserMixin
from database import db

class User(UserMixin, db.Model):
    """User model for storing user account information"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    default_units = db.Column(db.String(10), default='metric')  # 'metric' or 'imperial'
    
    # Relationships
    favorite_locations = db.relationship('FavoriteLocation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    search_history = db.relationship('SearchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class FavoriteLocation(db.Model):
    """Model for storing user's favorite locations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    added_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<FavoriteLocation {self.location_name}>'


class SearchHistory(db.Model):
    """Model for storing user's search history"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    searched_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchHistory {self.location_name}>'


class WeatherCache(db.Model):
    """Model for caching weather data"""
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(255), unique=True, nullable=False)
    data = db.Column(db.JSON, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        """Check if the cache entry is expired"""
        return datetime.datetime.utcnow() > self.expiry
    
    def __repr__(self):
        return f'<WeatherCache {self.cache_key}>'