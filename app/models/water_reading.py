from app import db
from datetime import datetime

class WaterReading(db.Model):
    __tablename__ = 'water_readings' # Must match your Entry Site's table name

    id = db.Column(db.Integer, primary_key=True)
    project_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Location & ID
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    pin_id = db.Column(db.String(50))
    image_url = db.Column(db.String(500))

    # All Sensors (Ocean + Pond)
    ph = db.Column(db.Float)
    tds = db.Column(db.Float)
    temperature = db.Column(db.Float)
    do = db.Column(db.Float)          # Pond Specific
    chlorophyll = db.Column(db.Float) # Pond Specific
    ta = db.Column(db.Float)          # Ocean Specific
    dic = db.Column(db.Float)         # Ocean Specific

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
