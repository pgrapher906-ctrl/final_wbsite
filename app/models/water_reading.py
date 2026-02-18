from . import db

class WaterReading(db.Model):
    __tablename__ = 'water_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    project_type = db.Column(db.String(20), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    pin_id = db.Column(db.String(50), nullable=False)
    
    ph = db.Column(db.Float)
    tds = db.Column(db.Float)
    temp = db.Column(db.Float)
    do = db.Column(db.Float, nullable=True)
    
    image_url = db.Column(db.String(500))

    def __repr__(self):
        return f'<{self.project_type} Reading {self.pin_id}>'
