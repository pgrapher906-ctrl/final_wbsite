from app import db
from sqlalchemy.sql import func

# This model must match your Data Entry website EXACTLY
class WaterData(db.Model):
    __tablename__ = "water_data"  # MATCHED: The table name from your first website

    id = db.Column(db.Integer, primary_key=True)
    
    # We map user_id even if we don't use it, to avoid SQLAlchemy errors
    user_id = db.Column(db.Integer, nullable=True) 

    # MATCHED: Auto-timestamp
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # MATCHED: Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # MATCHED: Identifiers
    water_type = db.Column(db.String(100), nullable=False) # Was 'project_type'
    pin_id = db.Column(db.String(100), nullable=False)

    # MATCHED: Sensor Data
    temperature = db.Column(db.Float)
    ph = db.Column(db.Numeric(4, 2))
    tds = db.Column(db.Float)
    do = db.Column(db.Float) # Only 'do' exists in your source model

    # MATCHED: Image path
    image_path = db.Column(db.String(300)) # Was 'image_url'

    def to_dict(self):
        # Helper to convert data to JSON
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'water_type': self.water_type,
            'pin_id': self.pin_id,
            'temperature': self.temperature,
            'ph': float(self.ph) if self.ph else 0.0, # Convert Decimal to float
            'tds': self.tds,
            'do': self.do,
            'image_path': self.image_path
        }

