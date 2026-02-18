import os
from app import create_app, db

app = create_app(os.getenv("FLASK_ENV", "production"))

@app.route('/seed')
def seed_data():
    """Route to seed data since Shell is not available on Free tier"""
    from app.models.water_reading import WaterReading
    import random
    from datetime import datetime, timedelta

    WaterReading.query.delete()
    projects = ['Ocean', 'Pond']
    for i in range(50):
        proj = random.choice(projects)
        r = WaterReading(
            project_type=proj,
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0,10)),
            latitude=17.3850 + random.uniform(-0.2, 0.2),
            longitude=78.4867 + random.uniform(-0.2, 0.2),
            pin_id=f"NRSC-{random.randint(100,999)}",
            ph=round(random.uniform(7.0, 8.5), 2),
            tds=random.randint(200, 500),
            temperature=round(random.uniform(25.0, 31.0), 1),
            chlorophyll=round(random.uniform(0.1, 5.0), 2),
            image_url="https://via.placeholder.com/150/0A3D62/FFFFFF?text=Water+Sample"
        )
        if proj == 'Ocean':
            r.ta, r.dic = 2250.0, 2100.0
        else:
            r.do = 7.2
        db.session.add(r)
    db.session.commit()
    return "✅ Database Seeded with 50 Professional Records!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
