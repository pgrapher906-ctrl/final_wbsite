import pandas as pd
from io import BytesIO
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file, jsonify
from app import db
from app.models.user import User
from app.models.water_reading import WaterData  # UPDATED IMPORT
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
        # Check if user exists using the User model (which links to 'users' table)
        if User.query.filter_by(username=request.form.get('username')).first():
             return render_template('register.html', error="User already exists")
             
        user = User(username=request.form.get('username'), email=request.form.get('email'))
        user.set_password(request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

# --- Login ---
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username')).first()
        if u and u.check_password(request.form.get('password')):
            u.visit_count += 1
            u.last_login = datetime.now() # Simplified time
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

# --- DATA FETCHING (FIXED) ---
@main_bp.route('/api/data')
@login_required
def get_data():
    proj = request.args.get('project', 'Ocean')
    
    # We use 'WaterData' model and 'water_type' column now
    if proj == 'Ocean':
        readings = WaterData.query.filter(
            or_(
                WaterData.water_type.ilike('%Ocean%'),
                WaterData.water_type.ilike('%Sea%'),
                WaterData.water_type.ilike('%Marine%'),
                WaterData.water_type.ilike('%Coastal%')
            )
        ).all()
    else:
        readings = WaterData.query.filter(
            or_(
                WaterData.water_type.ilike('%Pond%'),
                WaterData.water_type.ilike('%Drinking%'),
                WaterData.water_type.ilike('%Ground%')
            )
        ).all()
        
    return jsonify([r.to_dict() for r in readings])

# --- Excel Export ---
@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    if project == 'Ocean':
        readings = WaterData.query.filter(
            or_(WaterData.water_type.ilike('%Ocean%'), WaterData.water_type.ilike('%Sea%'))
        ).all()
    else:
        readings = WaterData.query.filter(
            or_(WaterData.water_type.ilike('%Pond%'), WaterData.water_type.ilike('%Ground%'))
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
    return send_file(output, as_attachment=True, download_name=f"AquaFlow_{project}.xlsx")

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
