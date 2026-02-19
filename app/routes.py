import pandas as pd
import base64
from io import BytesIO
from datetime import datetime
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.water_reading import WaterData
from openpyxl import Workbook

main_bp = Blueprint('main', __name__)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username')).first()
        if u and u.check_password(request.form.get('password')):
            # Update user session stats for the navbar
            u.visit_count = (u.visit_count or 0) + 1
            db.session.commit()
            login_user(u)
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    ocean_group = ['Open Ocean Water', 'Coastal Water', 'Estuarine Water', 'Deep Sea Water', 'Marine Surface Water']
    is_pond = project == "Pond" or project == "Pond Water"
    
    if project == "Ocean":
        readings = WaterData.query.filter(WaterData.water_type.in_(ocean_group)).all()
    elif is_pond:
        readings = WaterData.query.filter(WaterData.water_type == 'Pond Water').all()
    else:
        readings = WaterData.query.all()

    wb = Workbook()
    ws = wb.active
    
    # Headers with DO specifically for Pond reports
    headers = ['ID', 'Timestamp (IST)', 'Latitude', 'Longitude', 'Type', 'pH', 'Temp (°C)', 'TDS (PPM)']
    if is_pond:
        headers.insert(7, 'DO (PPM)')
    
    ws.append(headers)
    
    for r in readings:
        row = [r.id, r.timestamp.strftime('%Y-%m-%d %H:%M'), r.latitude, r.longitude, r.water_type, float(r.ph) if r.ph else 0.0, r.temperature]
        if is_pond:
            row.append(r.do) # Add DO for Freshwater
        row.append(r.tds)
        ws.append(row)

    # AUTO-FIX: Resize Excel columns so text like coordinates never hide
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            if cell.value and len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        ws.column_dimensions[column].width = max_length + 2
        
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name=f"Report.xlsx")

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/api/data')
@login_required
def get_data():
    readings = WaterData.query.order_by(WaterData.timestamp.desc()).all()
    return jsonify([r.to_dict() for r in readings])

@main_bp.route('/image/<int:record_id>')
@login_required
def get_image(record_id):
    r = WaterData.query.get(record_id)
    if r and r.image_path:
        img_data = r.image_path.split(",")[1] if "," in r.image_path else r.image_path
        return send_file(BytesIO(base64.b64decode(img_data)), mimetype='image/jpeg')
    return "Not found", 404

@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))
