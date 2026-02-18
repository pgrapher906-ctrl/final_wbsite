from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)

    # --- 1. Database Configuration ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # --- 2. THE CRITICAL FIX (Prevent SSL Disconnects) ---
    # This forces the app to "ping" the DB before every request.
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,  
        "pool_recycle": 300,    # Recycle connections every 5 minutes
    }

    # --- 3. Initialize App ---
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # --- 4. Register Blueprints ---
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # --- 5. Create Tables Automatically ---
    with app.app_context():
        db.create_all()

    return app
