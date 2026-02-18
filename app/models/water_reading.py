from app import db
from datetime import datetime

class WaterReading(db.Model):
    __tablename__ = 'water_readings'
    id = db.Column(db.Integer, primary_key=True)
    project_type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    pin_id = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    ph = db.Column(db.Float)
    tds = db.Column(db.Float)
    temperature = db.Column(db.Float)
    chlorophyll = db.Column(db.Float)
    ta = db.Column(db.Float) # Ocean specific
    dic = db.Column(db.Float) # Ocean specific
    do = db.Column(db.Float)  # Pond specific

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
