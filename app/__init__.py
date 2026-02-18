from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration (from config.py)
    from config import config
    app.config.from_object(config.get(config_name, config['default']))
    
    # Set secret key (Render / env safe)
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    )
    
    # Initialize database (Neon PostgreSQL)
    db.init_app(app)
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
