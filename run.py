import os, random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import WaterReading, User

app = create_app(os.getenv("FLASK_ENV", "development"))

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("✅ Database Tables Created!")

@app.cli.command("create-admin")
def create_admin():
    from app.models import User
    if User.query.filter_by(username='admin').first(): return
    admin = User(username='admin', email='admin@nrsc.gov.in')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin created: admin / admin123")

@app.cli.command("seed-db")
def seed_db():
    WaterReading.query.delete()
    for i in range(50):
        proj = random.choice(['Ocean', 'Pond'])
        r = WaterReading(
            project_type=proj,
            timestamp=datetime.utcnow() - timedelta(days=random.randint(0,10)),
            latitude=17.3 + random.uniform(-0.5, 0.5),
            longitude=78.4 + random.uniform(-0.5, 0.5),
            pin_id=f"NRSC-{random.randint(100,999)}",
            ph=round(random.uniform(7, 8), 2),
            tds=random.randint(200, 500),
            temperature=round(random.uniform(25, 30), 1),
            chlorophyll=round(random.uniform(0, 5), 2),
            image_url="https://via.placeholder.com/50"
        )
        if proj == 'Ocean': r.ta, r.dic = 2200, 2000
        else: r.do = 6.5
        db.session.add(r)
    db.session.commit()
    print("✅ Seeded 50 records!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
