from app import db
from datetime import datetime

class WaterReading(db.Model):
    """Model for water quality readings from IoT sensors"""
    __tablename__ = 'water_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    water_type = db.Column(db.String(50), nullable=False)  # drinking, groundwater, ocean
    chlorophyll = db.Column(db.Float, nullable=True)  # mg/L
    pigments = db.Column(db.Float, nullable=True)  # mg/L
    total_alkalinity = db.Column(db.Float, nullable=True)  # mg/L as CaCO3
    dic = db.Column(db.Float, nullable=True)  # Dissolved Inorganic Carbon, mmol/L
    temperature = db.Column(db.Float, nullable=True)  # Celsius
    sensor_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'date': self.timestamp.strftime('%Y-%m-%d'),
            'time': self.timestamp.strftime('%H:%M:%S'),
            'latitude': round(self.latitude, 6),
            'longitude': round(self.longitude, 6),
            'water_type': self.water_type,
            'chlorophyll': self.chlorophyll,
            'pigments': self.pigments,
            'total_alkalinity': self.total_alkalinity,
            'dic': self.dic,
            'temperature': self.temperature,
            'sensor_id': self.sensor_id
        }
    
    def __repr__(self):
        return f'<WaterReading {self.id} - {self.timestamp}>'
