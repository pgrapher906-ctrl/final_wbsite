import pandas as pd
from io import BytesIO
from flask import Blueprint, render_template, request, session, redirect, url_for, send_file, jsonify
from app import db
from app.models.user import User
from app.models.water_reading import WaterReading
from datetime import datetime
from functools import wraps

main_bp = Blueprint('main', __name__)

# ==================== Authentication Decorator ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Authentication Routes ====================

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            user.visit_count += 1
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            session.update({
                'user_id': user.id, 
                'username': user.username,
                'visit_count': user.visit_count,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M')
            })
            return redirect(url_for('main.index'))
        else:
            return render_template('login.html', error="Invalid username or password")
            
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists")
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error="Registration failed. Try again.")
            
    return render_template('register.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

# ==================== Dashboard Routes ====================

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/api/data')
@login_required
def get_data():
    project = request.args.get('project', 'Ocean')
    readings = WaterReading.query.filter_by(project_type=project).all()
    return jsonify([r.to_dict() for r in readings])

@main_bp.route('/export/<project>')
@login_required
def export_excel(project):
    readings = WaterReading.query.filter_by(project_type=project).all()
    data = [r.to_dict() for r in readings]
    
    if not data:
        return "No data available to export", 404
        
    df = pd.DataFrame(data)
    
    # Cleaning up the timestamp for Excel
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Water_Monitoring_Data')
    
    output.seek(0)
    return send_file(
        output, 
        as_attachment=True, 
        download_name=f"NRSC_{project}_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
