from flask import Blueprint, render_template, request, redirect, url_for, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models.user import User
from app.models.water_reading import WaterData
from openpyxl import Workbook
from io import BytesIO
import os

main_bp = Blueprint('main', __name__)

# FIX: Added Register Route to solve BuildError
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        if User.query.filter((User.email == email) | (User.username == username)).first():
            return render_template('register.html', error="User already exists.")
        
        new_user = User(username=username, email=email)
        new_user.set_password(request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username')).first()
        if u and u.check_password(request.form.get('password')):
            # Update Login Stats
            u.visit_count = (u.visit_count or 0) + 1
            u.last_login = datetime.now().strftime("%d-%m-%Y %H:%M")
            db.session.commit()
            login_user(u)
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    ocean_group = ['Open Ocean Water', 'Coastal Water', 'Estuarine Water', 'Deep Sea Water', 'Marine Surface Water']
    is_pond = project == "Pond"
    
    if project == "Ocean":
        readings = WaterData.query.filter(WaterData.water_type.in_(ocean_group)).all()
        headers = ['ID', 'Timestamp', 'Lat', 'Lon', 'Type', 'pH', 'Temp', 'TDS']
    elif is_pond:
        readings = WaterData.query.filter(WaterData.water_type == 'Pond Water').all()
        headers = ['ID', 'Timestamp', 'Lat', 'Lon', 'Type', 'pH', 'Temp', 'DO (PPM)', 'TDS']
    else:
        readings = WaterData.query.all()
        headers = ['ID', 'Timestamp', 'Lat', 'Lon', 'Type', 'pH', 'Temp', 'DO', 'TDS']

    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    
    for r in readings:
        row = [r.id, r.timestamp.strftime('%Y-%m-%d %H:%M'), r.latitude, r.longitude, r.water_type, r.ph, r.temperature]
        if project != "Ocean":
            row.append(r.do)
        row.append(r.tds)
        ws.append(row)

    # Auto-adjust column widths
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 15
        
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name=f"NRSC_{project}_Report.xlsx")

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/api/data')
@login_required
def get_data():
    readings = WaterData.query.order_by(WaterData.timestamp.desc()).all()
    return jsonify([r.to_dict() for r in readings])

@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))
