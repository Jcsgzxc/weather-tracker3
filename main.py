import logging
from app import app
from database import db
import models  # Import models to create tables

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    logging.debug("Database tables created")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
