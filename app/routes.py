from flask import Blueprint, render_template, request, redirect, url_for, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models.user import User
from app.models.water_reading import WaterData
from openpyxl import Workbook
from io import BytesIO

main_bp = Blueprint('main', __name__)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form.get('username')).first()
        if u and u.check_password(request.form.get('password')):
            u.visit_count = (u.visit_count or 0) + 1
            u.last_login = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            db.session.commit()
            login_user(u)
            return redirect(url_for('main.index'))
    return render_template('login.html')

@main_bp.route('/api/data')
@login_required
def get_data():
    readings = WaterData.query.order_by(WaterData.timestamp.desc()).all()
    return jsonify([r.to_dict() for r in readings])

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))
