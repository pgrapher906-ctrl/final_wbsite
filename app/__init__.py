from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Automatically creates all necessary tables in Neon on startup
    with app.app_context():
        from app.models.user import User
        from app.models.water_reading import WaterReading
        db.create_all() 

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
