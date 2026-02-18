from flask import Blueprint, render_template, redirect, url_for, request, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models.user import db, User
from .models.water_reading import WaterReading
import pandas as pd
from io import BytesIO
from datetime import datetime

main = Blueprint('main', __name__)

# --- Authentication Routes ---
@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('main.register'))
            
        new_user = User(
            username=username, 
            email=email, 
            password=generate_password_hash(password, method='sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            # Update User Stats
            user.visit_count += 1
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid login credentials')
            
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- Dashboard & Functional Routes ---
@main.route('/dashboard')
@login_required
def dashboard():
    # Default to Ocean if no project selected
    project_type = request.args.get('project', 'Ocean')
    
    # Filter data based on selection
    readings = WaterReading.query.filter_by(project_type=project_type).all()
    
    return render_template('index.html', data=readings, current_project=project_type)

@main.route('/export/<project_type>')
@login_required
def export_data(project_type):
    readings = WaterReading.query.filter_by(project_type=project_type).all()
    
    if not readings:
        return redirect(url_for('main.dashboard'))

    # Create DataFrame
    data_list = []
    for r in readings:
        row = {
            'Date': r.date,
            'Time': r.time,
            'Type': r.project_type,
            'Lat': r.lat,
            'Lon': r.lon,
            'Pin ID': r.pin_id,
            'pH': r.ph,
            'TDS': r.tds,
            'Temp': r.temp,
            'Image': r.image_url
        }
        if project_type == 'Pond':
            row['DO'] = r.do
        data_list.append(row)

    df = pd.DataFrame(data_list)
    
    # Export to Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=project_type)
    output.seek(0)
    
    return send_file(
        output, 
        download_name=f"{project_type}_Data.xlsx", 
        as_attachment=True
    )
