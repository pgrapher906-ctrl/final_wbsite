from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
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
    project_type = db.Column(db.String(20), nullable=False) # 'Ocean' or 'Pond'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    pin_id = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    
    # Parameters
    ph = db.Column(db.Float)
    tds = db.Column(db.Float)
    temperature = db.Column(db.Float)
    chlorophyll = db.Column(db.Float)
    ta = db.Column(db.Float) # Ocean Specific
    dic = db.Column(db.Float) # Ocean Specific
    do = db.Column(db.Float) # Pond Specific

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
