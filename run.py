import os
from app import create_app, db

# Create Flask application
app = create_app(os.getenv("FLASK_ENV", "development"))

@app.shell_context_processor
def make_shell_context():
    """Create shell context for Flask CLI"""
    return {'db': db}

@app.cli.command()
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print('Database initialized (Neon PostgreSQL).')

@app.cli.command()
def drop_db():
    """Drop all database tables"""
    if input('Are you sure? (y/n): ').lower() == 'y':
        with app.app_context():
            db.drop_all()
            print('Database dropped.')

@app.cli.command()
def seed_db():
    """Seed database with sample data"""
    from app.models import WaterReading
    from datetime import datetime, timedelta
    import random

    water_types = ['drinking', 'groundwater', 'ocean']
    sensor_ids = ['SENSOR-001', 'SENSOR-002', 'SENSOR-003']

    locations = [
        (40.7128, -74.0060),   # New York
        (51.5074, -0.1278),    # London
        (35.6762, 139.6503),   # Tokyo
        (48.8566, 2.3522),     # Paris
        (37.7749, -122.4194),  # San Francisco
    ]

    base_date = datetime.utcnow() - timedelta(days=7)

    with app.app_context():
        for i in range(50):
            timestamp = base_date + timedelta(hours=random.randint(0, 168))
            lat, lon = random.choice(locations)

            reading = WaterReading(
                timestamp=timestamp,
                latitude=lat + random.uniform(-0.1, 0.1),
                longitude=lon + random.uniform(-0.1, 0.1),
                water_type=random.choice(water_types),
                chlorophyll=round(random.uniform(0.1, 50.0), 2),
                pigments=round(random.uniform(0.05, 30.0), 2),
                total_alkalinity=round(random.uniform(50.0, 200.0), 2),
                dic=round(random.uniform(1.0, 5.0), 2),
                temperature=round(random.uniform(5.0, 35.0), 1),
                sensor_id=random.choice(sensor_ids)
            )
            db.session.add(reading)

        db.session.commit()
        print('Database seeded with 50 sample readings (Neon PostgreSQL).')

@app.cli.command()
def create_admin():
    """Create default admin user for login"""
    from app.models import User

    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print('Admin user already exists!')
            return

        admin_user = User(username='admin')
        admin_user.set_password('admin')
        db.session.add(admin_user)
        db.session.commit()

        print('✓ Admin user created successfully!')
        print('Username: admin')
        print('Password: admin')
        print('⚠️ IMPORTANT: Change this password in production!')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
