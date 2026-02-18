from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, send_file
from app import db
from app.models.user import User
from app.models.water_reading import WaterReading
from datetime import datetime
from functools import wraps
import pandas as pd
from io import BytesIO

main_bp = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

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
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists")
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main.login'))
        except Exception:
            db.session.rollback()
            return render_template('register.html', error="Registration failed.")
    return render_template('register.html')

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
