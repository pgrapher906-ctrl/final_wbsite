import pandas as pd
from io import BytesIO
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file, jsonify
from app import db
from app.models.user import User
from app.models.water_reading import WaterReading
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

# --- Registration ---
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form.get('username'), email=request.form.get('email'))
        user.set_password(request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

# --- Login & Tracking ---
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username')).first()
        if u and u.check_password(request.form.get('password')):
            u.visit_count += 1
            u.last_login = datetime.utcnow()
            db.session.commit()
            session.update({
                'user_id': u.id, 'username': u.username,
                'visit_count': u.visit_count,
                'last_login': u.last_login.strftime('%Y-%m-%d %H:%M')
            })
            return redirect(url_for('main.index'))
    return render_template('login.html')

# --- Dashboard ---
@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

# --- FIXED DATA FETCHING ---
@main_bp.route('/api/data')
@login_required
def get_data():
    proj = request.args.get('project', 'Ocean')
    
    if proj == 'Ocean':
        # Searches for ANY entry containing "Ocean", "Sea", "Marine", or "Coastal"
        readings = WaterReading.query.filter(
            or_(
                WaterReading.project_type.ilike('%Ocean%'),
                WaterReading.project_type.ilike('%Sea%'),
                WaterReading.project_type.ilike('%Marine%'),
                WaterReading.project_type.ilike('%Coastal%'),
                WaterReading.project_type.ilike('%Estuarine%')
            )
        ).all()
    else:
        # Searches for ANY entry containing "Pond", "Drinking", or "Ground"
        readings = WaterReading.query.filter(
            or_(
                WaterReading.project_type.ilike('%Pond%'),
                WaterReading.project_type.ilike('%Drinking%'),
                WaterReading.project_type.ilike('%Ground%')
            )
        ).all()
        
    return jsonify([r.to_dict() for r in readings])

# --- Excel Export ---
@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    # Apply the same flexible search for the Excel export
    if project == 'Ocean':
        readings = WaterReading.query.filter(
            or_(
                WaterReading.project_type.ilike('%Ocean%'),
                WaterReading.project_type.ilike('%Sea%'),
                WaterReading.project_type.ilike('%Marine%'),
                WaterReading.project_type.ilike('%Coastal%')
            )
        ).all()
    else:
        readings = WaterReading.query.filter(
            or_(WaterReading.project_type.ilike('%Pond%'), WaterReading.project_type.ilike('%Drinking%'))
        ).all()

    data = []
    for r in readings:
        row = r.to_dict()
        if r.timestamp:
            row['Date'] = r.timestamp.strftime('%Y-%m-%d')
            row['Time'] = r.timestamp.strftime('%H:%M:%S')
        data.append(row)
        
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"AquaFlow_{project}_Report.xlsx")

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
