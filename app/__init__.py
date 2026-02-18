from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        # Load models so SQLAlchemy knows the schema
        from app.models.user import User
        from app.models.water_reading import WaterReading
        
        # This ensures the viewer can 'see' the tables created by the entry site
        db.create_all()

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
