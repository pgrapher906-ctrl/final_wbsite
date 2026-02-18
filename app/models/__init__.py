from flask import Flask
from flask_login import LoginManager
from .models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    # Move Model Imports HERE (Inside the function)
    # This breaks the circular loop
    from .models.user import User
    from .models.water_reading import WaterReading

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Create tables
    with app.app_context():
        db.create_all()

    return app
