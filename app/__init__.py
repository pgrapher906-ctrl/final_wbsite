from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)

    # 1. Configuration (Uses your Secret Key and Neon URL)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smart_water_2026_secure_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Keeps connection alive on Render (Prevents SSL Errors)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # 2. Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # 3. User Loader (The "Bridge" to the Dashboard)
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 4. Register Routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()

    return app
