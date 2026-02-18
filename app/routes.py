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
        if User.query.filter_by(username=request.form.get('username')).first():
             return render_template('register.html', error="User already exists")
             
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
            u.last_login = datetime.now()
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

# --- DATA FETCHING ---
@main_bp.route('/api/data')
@login_required
def get_data():
    proj = request.args.get('project', 'Ocean')
    
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

# --- IMAGE SERVING ROUTE (UPDATED FOR BASE64) ---
@main_bp.route('/image/<int:record_id>')
@login_required
def get_image(record_id):
    # Find the record by ID
    record = WaterData.query.get(record_id)
    
    # Check if record exists and has image data
    if record and record.image_path:
        try:
            image_text = record.image_path
            
            # If stored as data URI (e.g., "data:image/jpeg;base64,..."), strip the header
            if "," in image_text:
                image_text = image_text.split(",")[1]
                
            # Decode Base64 Text -> Binary Image
            img_bytes = base64.b64decode(image_text)
            
            return send_file(
                BytesIO(img_bytes),
                mimetype='image/jpeg',
                as_attachment=False,
                download_name=f"image_{record_id}.jpg"
            )
        except Exception as e:
            print(f"Error decoding image: {e}")
            return "Image Error", 500
    
    return "Image not found", 404

# --- Excel Export ---
@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    if project == 'Ocean':
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

    data = []
    for r in readings:
        row = r.to_dict()
        if r.timestamp:
            row['Date'] = r.timestamp.strftime('%Y-%m-%d')
            row['Time'] = r.timestamp.strftime('%H:%M:%S')
        
        row['image_path'] = "Image Available" if row.get('image_path') else "No Image"
        
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
