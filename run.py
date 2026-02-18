import os
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import WaterReading, User

app = create_app(os.getenv("FLASK_ENV", "development"))

@app.cli.command("seed-db")
def seed_db():
    """Seeds the Neon PostgreSQL database with professional sample data"""
    print("Deleting old data...")
    WaterReading.query.delete()
    
    projects = ['Ocean', 'Pond']
    
    # Coordinates for sample locations (e.g., coastal regions for Ocean, inland for Pond)
    locations = [
        (17.3850, 78.4867), # Hyderabad area
        (13.0827, 80.2707), # Chennai (Coastal)
        (19.0760, 72.8777), # Mumbai (Coastal)
    ]

    print("Generating 50 professional readings...")
    for i in range(50):
        project = random.choice(projects)
        lat, lon = random.choice(locations)
        
        reading = WaterReading(
            project_type=project,
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
            latitude=lat + random.uniform(-0.1, 0.1),
            longitude=lon + random.uniform(-0.1, 0.1),
            pin_id=f"NRSC-{random.randint(1000, 9999)}",
            ph=round(random.uniform(6.5, 8.5), 2),
            tds=round(random.uniform(100, 500), 2),
            temperature=round(random.uniform(22.0, 32.0), 1),
            chlorophyll=round(random.uniform(0.1, 10.0), 2),
            image_url="https://via.placeholder.com/150/0A3D62/FFFFFF?text=Water+Sample"
        )

        # Add project-specific data
        if project == 'Ocean':
            reading.ta = round(random.uniform(2000, 2500), 2)
            reading.dic = round(random.uniform(1800, 2200), 2)
        else:
            reading.do = round(random.uniform(4.0, 9.0), 2)

        db.session.add(reading)

    db.session.commit()
    print("✅ Database successfully seeded with 50 readings!")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
