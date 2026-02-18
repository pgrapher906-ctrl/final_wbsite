import os, random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.water_reading import WaterReading

app = create_app(os.getenv("FLASK_ENV", "production"))

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("✅ Neon Database Tables Created!")

@app.cli.command("create-admin")
def create_admin():
    if User.query.filter_by(username='admin').first():
        print("Admin exists.")
        return
    admin = User(username='admin', email='admin@nrsc.gov.in')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin Created: admin / admin123")

@app.cli.command("seed-db")
def seed_db():
    WaterReading.query.delete()
    projects = ['Ocean', 'Pond']
    for i in range(50):
        proj = random.choice(projects)
        r = WaterReading(
            project_type=proj,
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0,10)),
            latitude=17.3850 + random.uniform(-0.5, 0.5),
            longitude=78.4867 + random.uniform(-0.5, 0.5),
            pin_id=f"NRSC-{random.randint(100,999)}",
            ph=round(random.uniform(7.0, 8.5), 2),
            tds=random.randint(200, 500),
            temperature=round(random.uniform(25.0, 31.0), 1),
            chlorophyll=round(random.uniform(0.1, 5.0), 2),
            image_url="https://via.placeholder.com/150/0A3D62/FFFFFF?text=NRSC+Sample"
        )
        if proj == 'Ocean':
            r.ta, r.dic = 2250.0, 2100.0
        else:
            r.do = 7.2
        db.session.add(r)
    db.session.commit()
    print("✅ Seeded 50 professional records!")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
