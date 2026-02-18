from app import db
from sqlalchemy.sql import func

class WaterData(db.Model):
    __tablename__ = "water_data"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    water_type = db.Column(db.String(100), nullable=False)
    pin_id = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    ph = db.Column(db.Numeric(4, 2))
    tds = db.Column(db.Float)
    do = db.Column(db.Float)

    # 🔥 UPDATED: Must be db.Text to hold Base64 strings
    image_path = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'water_type': self.water_type,
            'pin_id': self.pin_id,
            'temperature': self.temperature,
            'ph': float(self.ph) if self.ph else 0.0,
            'tds': self.tds,
            'do': self.do,
            # We return just a flag to the frontend, not the huge string
            'image_path': "Image Available" if self.image_path else None
        }
