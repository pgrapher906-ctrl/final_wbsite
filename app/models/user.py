from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    visit_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class WaterReading(db.Model):
    __tablename__ = 'water_readings'
    id = db.Column(db.Integer, primary_key=True)
    project_type = db.Column(db.String(20), nullable=False)  # 'Ocean' or 'Pond'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    pin_id = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    
    # Shared & Specific Parameters
    ph = db.Column(db.Float)
    tds = db.Column(db.Float)
    temperature = db.Column(db.Float)
    chlorophyll = db.Column(db.Float)
    ta = db.Column(db.Float)  # Ocean
    dic = db.Column(db.Float) # Ocean
    do = db.Column(db.Float)  # Pond

    def to_dict(self):
        return {
            "date": self.timestamp.strftime('%Y-%m-%d'),
            "time": self.timestamp.strftime('%H:%M:%S'),
            "project_type": self.project_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "pin_id": self.pin_id,
            "ph": self.ph,
            "tds": self.tds,
            "temperature": self.temperature,
            "chlorophyll": self.chlorophyll,
            "ta": self.ta,
            "dic": self.dic,
            "do": self.do,
            "image": self.image_url
        }
