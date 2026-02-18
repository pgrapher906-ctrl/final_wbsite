# FILE: app/__init__.py
from flask import Flask
from flask_login import LoginManager
from .models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize Database
    db.init_app(app)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    # Import models HERE to avoid circular imports
    from .models.user import User
    from .models.water_reading import WaterReading

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Routes
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Create Tables automatically
    with app.app_context():
        db.create_all()

    return app
