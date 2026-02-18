import pandas as pd
import base64
from io import BytesIO
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file, jsonify
from app import db
from app.models.user import User
from app.models.water_reading import WaterData
from datetime import datetime
from functools import wraps
from sqlalchemy import or_
from openpyxl import Workbook

main_bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email, user = request.form.get('email'), request.form.get('username')
        if User.query.filter((User.email == email) | (User.username == user)).first():
            return render_template('register.html', error="User already exists.")
        try:
            new_u = User(username=user, email=email)
            new_u.set_password(request.form.get('password'))
            db.session.add(new_u); db.session.commit()
            return redirect(url_for('main.login'))
        except: return render_template('register.html', error="Registration Error.")
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username')).first()
        if u and u.check_password(request.form.get('password')):
            session.update({'user_id': u.id, 'username': u.username})
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/api/data')
@login_required
def get_data():
    readings = WaterData.query.all()
    return jsonify([r.to_dict() for r in readings])

@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    readings = WaterData.query.all()
    wb = Workbook()
    ws = wb.active
    ws.append(['ID', 'Time', 'Lat', 'Lon', 'Type', 'pH', 'TDS', 'Temp'])
    for r in readings:
        ws.append([r.id, r.timestamp.strftime('%Y-%m-%d %H:%M'), r.latitude, r.longitude, r.water_type, float(r.ph), r.tds, r.temperature])
    output = BytesIO()
    wb.save(output); output.seek(0)
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="AquaFlow_Data.xlsx")

@main_bp.route('/image/<int:record_id>')
@login_required
def get_image(record_id):
    r = WaterData.query.get(record_id)
    if r and r.image_path:
        img_data = r.image_path.split(",")[1] if "," in r.image_path else r.image_path
        return send_file(BytesIO(base64.b64decode(img_data)), mimetype='image/jpeg')
    return "Not found", 404

@main_bp.route('/')
@login_required
def index(): return render_template('index.html')

@main_bp.route('/logout')
def logout(): session.clear(); return redirect(url_for('main.login'))
