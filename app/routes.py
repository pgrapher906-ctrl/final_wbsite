from flask import Blueprint, render_template, request, redirect, url_for, send_file, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models.user import User
from app.models.water_reading import WaterData
from openpyxl import Workbook
from io import BytesIO

main_bp = Blueprint('main', __name__)

# RESTORED: Route to open images based on reading ID
@main_bp.route('/image/<int:id>')
@login_required
def get_image(id):
    reading = WaterData.query.get_or_404(id)
    if not reading.image_data:
        abort(404)
    return send_file(BytesIO(reading.image_data), mimetype='image/jpeg')

# RESTORED: Excel Export with DO (PPM)
@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    ocean_group = ['Open Ocean Water', 'Coastal Water', 'Estuarine Water', 'Deep Sea Water', 'Marine Surface Water']
    pond_group = ['Pond Water', 'Drinking Water', 'Ground Water', 'Borewell Water']
    
    if project == "Ocean":
        readings = WaterData.query.filter(WaterData.water_type.in_(ocean_group)).all()
    elif project == "Pond":
        readings = WaterData.query.filter(WaterData.water_type.in_(pond_group)).all()
    else:
        readings = WaterData.query.all()

    wb = Workbook()
    ws = wb.active
    ws.append(['ID', 'Timestamp', 'Lat', 'Lon', 'Type', 'PH', 'DO (PPM)', 'TDS', 'TEMP'])
    for r in readings:
        ws.append([r.id, r.timestamp.strftime('%Y-%m-%d %H:%M'), r.latitude, r.longitude, r.water_type, r.ph, r.do, r.tds, r.temperature])
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name=f"NRSC_{project}_Report.xlsx")

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username')).first()
        if u and u.check_password(request.form.get('password')):
            u.visit_count = (u.visit_count or 0) + 1
            u.last_login = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            db.session.commit()
            login_user(u)
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/api/data')
@login_required
def get_data():
    readings = WaterData.query.order_by(WaterData.timestamp.desc()).all()
    return jsonify([r.to_dict() for r in readings])

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')
