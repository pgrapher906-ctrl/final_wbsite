import pandas as pd
import base64
from io import BytesIO
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file, jsonify, flash
from app import db
from app.models.user import User
from app.models.water_reading import WaterData
from datetime import datetime
from functools import wraps
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Registration (FIXED: Prevents 500 error on duplicate email) ---
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        
        # Check if user already exists
        user_exists = User.query.filter((User.email == email) | (User.username == username)).first()
        if user_exists:
            return render_template('register.html', error="Email or Username already registered.")
             
        try:
            user = User(username=username, email=email)
            user.set_password(request.form.get('password'))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error="Database error. Please try again.")

    return render_template('register.html')

# --- Login & Tracking ---
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username')).first()
        if u and u.check_password(request.form.get('password')):
            u.visit_count += 1
            u.last_login = datetime.now()
            db.session.commit()
            session.update({
                'user_id': u.id, 'username': u.username,
                'visit_count': u.visit_count,
                'last_login': u.last_login.strftime('%Y-%m-%d %H:%M')
            })
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/api/data')
@login_required
def get_data():
    proj = request.args.get('project', 'Ocean')
    
    # Query without loading the heavy image_path column initially
    query = WaterData.query
    if proj == 'Ocean':
        readings = query.filter(or_(WaterData.water_type.ilike('%Ocean%'), WaterData.water_type.ilike('%Sea%'))).all()
    else:
        readings = query.filter(or_(WaterData.water_type.ilike('%Pond%'), WaterData.water_type.ilike('%Drinking%'))).all()
        
    return jsonify([r.to_dict() for r in readings])

@main_bp.route('/image/<int:record_id>')
@login_required
def get_image(record_id):
    record = WaterData.query.get(record_id)
    if record and record.image_path:
        try:
            image_text = record.image_path
            if "," in image_text:
                image_text = image_text.split(",")[1]
            img_bytes = base64.b64decode(image_text)
            return send_file(BytesIO(img_bytes), mimetype='image/jpeg')
        except:
            return "Image Error", 500
    return "Not found", 404

# --- Excel Export (FIXED for Vercel/Memory Efficiency) ---
@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    from openpyxl import Workbook
    
    if project == 'Ocean':
        readings = WaterData.query.filter(WaterData.water_type.ilike('%Ocean%')).all()
    else:
        readings = WaterData.query.filter(WaterData.water_type.ilike('%Pond%')).all()

    # Build Excel manually for speed and memory
    wb = Workbook()
    ws = wb.active
    ws.title = "AquaFlow Data"
    
    # Headers
    headers = ['ID', 'Timestamp', 'Lat', 'Lon', 'Type', 'pH', 'TDS', 'Temp', 'DO']
    ws.append(headers)

    for r in readings:
        ws.append([
            r.id, 
            r.timestamp.strftime('%Y-%m-%d %H:%M') if r.timestamp else '',
            r.latitude, r.longitude, r.water_type, 
            float(r.ph) if r.ph else 0.0, r.tds, r.temperature, r.do
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"AquaFlow_{project}_Data.xlsx"
    )

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
